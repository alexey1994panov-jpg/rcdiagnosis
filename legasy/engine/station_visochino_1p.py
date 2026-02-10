from __future__ import annotations

from dataclasses import dataclass
from typing import List, Dict

from engine.occupancy.exceptions.base import LzException, LsException
from engine.occupancy.exceptions.exc_local_mu import LocalMuException
from engine.occupancy.exceptions.exc_dsp_autoaction_timeout import (
    DspAutoActionTimeoutException,
)
from engine.occupancy.exceptions.exc_recent_ls_on_adjacent import (
    RecentLsOnAdjacentException,
)
from engine.occupancy.exceptions.exc_ls_local_mu import LsLocalMuException
from engine.occupancy.exceptions.exc_ls_after_lz import LsAfterLzException
from engine.occupancy.exceptions.exc_ls_dsp_autoaction import (
    LsDspAutoActionException,
)
from .config_1p import T_MU, T_RECENT_LS, T_MIN_MANEUVER_V8


# --- Объекты местного управления и автодействия ---


@dataclass
class StationRcMU:
    """
    Объект местного управления для РЦ.

    state:
      3 — индикатор не горит, местное управление выключено.
      4 — индикатор горит красным, местное управление включено (локальное).
    """

    id: str
    state: int = 3  # по умолчанию МУ выключено


@dataclass
class AutoAction:
    """
    Объект автодействия.

    state:
      3 — автодействие выключено (АС=0).
      4 — автодействие включено.
    rc_ids — список РЦ, на которые распространяется данное автодействие.
    """

    id: str
    state: int = 4  # по умолчанию включено
    rc_ids: List[str] | None = None

    def __post_init__(self) -> None:
        if self.rc_ids is None:
            self.rc_ids = []


# --- Модель станции ---


@dataclass
class StationModel1P:
    rc_ids: List[str]
    switch_ids: List[str]

    # контролируемая РЦ
    ctrl_rc_id: str

    # кандидаты для предыдущих и следующих РЦ относительно ctrl_rc_id
    prev_candidates: List[str]
    next_candidates: List[str]

    # стрелки, влияющие на связи ctrl_rc_id <-> соседние РЦ
    # для нашего участка: Sw10, Sw1, Sw5
    main_switch_id: str  # основная стрелка (Sw10)
    aux_switch_ids: List[str]  # дополнительные (Sw1 и Sw5)

    # один объект местного управления, на который ссылаются все РЦ
    rc_mu: StationRcMU

    # ссылка РЦ -> объект местного управления
    rc_mu_by_rc: Dict[str, StationRcMU]

    # два объекта автодействия: Н Автодействие (НАС) и Ч Автодействие (ЧАС)
    auto_actions: List[AutoAction]

    # режим "Управление станцией от ДСП"
    # 3 — нет управления от ДСП; 4 — управление от ДСП активно
    dispatcher_control_state: int = 3

    # реестр исключений ЛЗ по РЦ: rc_id -> список исключений
    lz_exceptions_by_rc: Dict[str, List[LzException]] | None = None
    # реестр исключений ЛС по РЦ: rc_id -> список исключений
    ls_exceptions_by_rc: Dict[str, List[LsException]] | None = None

    # настройки исключений (дефолты из config_1p)
    t_mu: float = T_MU
    t_recent_ls: float = T_RECENT_LS
    t_min_maneuver_v8: float = T_MIN_MANEUVER_V8

    # опционально: признак главных / приёмо-отправочных путей
    main_rc_ids: List[str] | None = None

    # опционально: признак наличия замыкания по РЦ
    # (True — есть замыкание, False — нет)
    rc_has_route_lock: Dict[str, bool] | None = None

    # светофоры на участке
    # идентификаторы светофоров
    signal_ids: List[str] | None = None
    # привязка светофора к предыдущей РЦ (PrevSec в XML)
    signal_prev_by_id: Dict[str, str] | None = None
    # привязка светофора к следующей РЦ (NextSec в XML)
    signal_next_by_id: Dict[str, str] | None = None

    def get_lz_exceptions_for_rc(self, rc_id: str) -> List[LzException]:
        """
        Утилита для безопасного получения списка исключений ЛЗ для РЦ.
        """
        if self.lz_exceptions_by_rc is None:
            return []
        return self.lz_exceptions_by_rc.get(rc_id, [])

    def get_ls_exceptions_for_rc(self, rc_id: str) -> List[LsException]:
        """
        Утилита для безопасного получения списка исключений ЛС для РЦ.
        """
        if self.ls_exceptions_by_rc is None:
            return []
        return self.ls_exceptions_by_rc.get(rc_id, [])


# --- Базовая модель с контролируемой 1P ---


def get_station_model_1p() -> StationModel1P:
    """
    Жёстко зашитая модель участка 10-12СП – Sw10 – 1П – 1-7СП
    с учётом стрелок 1 и 5, входящих в 1-7СП.

    В данной конфигурации:
    - все три РЦ ("10-12SP", "1P", "1-7SP") имеют ссылку на один и тот же
      объект местного управления StationRcMU;
    - существуют два объекта автодействия: "NAS" и "CHAS", каждый из которых
      ссылается на все три РЦ;
    - на контролируемую РЦ 1P навешаны исключения ЛЗ и ЛС;
    - заведены светофоры, привязанные к этим РЦ и к соседним (возможным) РЦ.
    """
    # Расширённый список РЦ участка и смежных участков (минимально, без изменения семантики)
    rc_ids = [
        "10-12SP",
        "1P",
        "1-7SP",
        # смежные участки и указанные в Objects.xml
        "1AP",
        "NP",
        "2-8SP",
        "14-16SP",
        "3SP",
        "4SP",
        "6SP",
        "CHP",
        "NDP",
        "2AP",
        "2P",
        "3P",
        "4P",
        "CHDP",
    ]

    # общий объект местного управления для всех РЦ станции
    common_mu = StationRcMU(id="MU_ALL", state=3)

    # привязка МУ ко всем РЦ
    rc_mu_by_rc = {rc_id: common_mu for rc_id in rc_ids}

    # автодействия: списки РЦ под автодействием (по умолчанию — все rc_ids)
    nas_rc_ids = [
    "10-12SP",
    "1P",
    "1-7SP",
    "1AP",
    "NP",
    "4SP",
    "CHDP",
    ]

    chas_rc_ids = [
    "2-8SP",
    "14-16SP",
    "3SP",
    "6SP",
    "CHP",
    "NDP",
    "2AP",
    "2P",
    ]

    nas_rc_ids = list(rc_ids)
    chas_rc_ids = list(rc_ids)

    nas = AutoAction(id="NAS", state=4, rc_ids=nas_rc_ids)   # Н Автодействие
    chas = AutoAction(id="CHAS", state=4, rc_ids=chas_rc_ids) # Ч Автодействие

    # Признак замыкания по РЦ: по умолчанию False, для известных ранее РЦ сохраним старые значения
    rc_has_route_lock = {rc_id: False for rc_id in rc_ids}
    rc_has_route_lock.update({
        "10-12SP": False,
        "1P": True,
        "1-7SP": True,
    })

    # Стрелки (имена сохраняем с префиксом Sw..., соответствуя Object NAME)
    switch_ids = ["Sw1", "Sw2", "Sw3", "Sw4", "Sw5", "Sw6", "Sw10", "Sw16"]

    # Светофоры: синхронизированы с XML (взяты основные сигналы, используемые в детекторах)
    signal_ids = [
        "Ч",
        "ЧД",
        "Ч1",  # PrevSec: 1П -> NextSec: 1-7СП
        "Ч2",
        "Ч3",  
        "ЧМ1", # PrevSec: 1АП -> NextSec: 10-12СП
        "ЧМ2",
        "ЧМ4",
        "Н",
        "НД",
        "НМ1", # PrevSec: 1П -> NextSec: 10-12СП
        "НМ2",
        "НМ3",
        "Н1",
        "Н2",
        "Н4",
        "М1",  # PrevSec: ЧП -> NextSec: 1-7СП (кириллица)
        "M1",  # латинская M встречается в коде — дублируем для совместимости
        "М2",
        "М3",
        "М4"
    ]

    signal_prev_by_id = {
        "Ч": None,
        "ЧД": None,
        "Ч1": "1P",
        "Ч2": "2P",
        "Ч3": "3P",
        "ЧМ1": "1AP", 
        "ЧМ2": "2AP",
        "ЧМ4": "4AP",
        "Н": None,
        "НД": None,
        "НМ1": "1P",
        "НМ2": "2P",
        "НМ3": "3P",
        "Н1": "1AP",
        "Н2": "2AP",
        "Н4": "4AP",
        "М1": "NP",
        "M1": "NP",
        "М2": "CHP",
        "М3": "NDP",
        "М4": "CHDP",
    }

    signal_next_by_id = {
        "Ч": "CHP",
        "ЧД": "CHDP",
        "Ч1": "1-7SP",
        "Ч2": "3SP",
        "Ч3": "1-7SP",
        "ЧМ1": "10-12SP", 
        "ЧМ2": "14-16SP",
        "ЧМ4": "14-16SP",
        "Н": "NP",
        "НД": "NDP",
        "НМ1": "10-12SP",
        "НМ2": "14-16SP",
        "НМ3": "10-12SP",
        "Н1":  "4SP",
        "Н2": "6SP",
        "Н4":  "2-8SP",
        "М1": "10-12SP",
        "M1": "10-12SP",
        "М2": "2-8SP",
        "М3": "3SP",
        "М4": "4SP",
    }

    station = StationModel1P(
        rc_ids=rc_ids,
        switch_ids=switch_ids,
        ctrl_rc_id="1P",
        prev_candidates=["10-12SP"],
        next_candidates=["1-7SP"],
        main_switch_id="Sw10",
        aux_switch_ids=["Sw1", "Sw5"],
        rc_mu=common_mu,
        rc_mu_by_rc=rc_mu_by_rc,
        auto_actions=[nas, chas],
        dispatcher_control_state=3,
        lz_exceptions_by_rc={},  # заполним ниже
        ls_exceptions_by_rc={},  # заполним ниже
        main_rc_ids=["1P"],
        rc_has_route_lock=rc_has_route_lock,
        signal_ids=signal_ids,
        signal_prev_by_id=signal_prev_by_id,
        signal_next_by_id=signal_next_by_id,
    )

    # исключения ЛЗ для контролируемой РЦ (1P)
    station.lz_exceptions_by_rc = {
        station.ctrl_rc_id: [
            LocalMuException(),
            DspAutoActionTimeoutException(),
            RecentLsOnAdjacentException(),
        ]
    }

    # исключения ЛС для контролируемой РЦ (1P)
    station.ls_exceptions_by_rc = {
        station.ctrl_rc_id: [
            LsLocalMuException(),
            LsAfterLzException(),
            LsDspAutoActionException(),
        ]
    }

    return station


# --- Модель с контролируемой 10-12SP ---


def get_station_model_1012_ctrl() -> StationModel1P:
    """
    Модель того же участка, но с контролируемой РЦ 10-12SP.
    Используется в сценариях v4/v12 для 10-12СП.
    """
    base = get_station_model_1p()

    # смещаем контролируемую РЦ
    base.ctrl_rc_id = "10-12SP"
    base.prev_candidates = []          # слева нет соседей (край)
    base.next_candidates = ["1P"]      # справа 1P

    # переносим исключения ЛЗ/ЛС с 1P на 10-12SP
    lz_from_1p = base.get_lz_exceptions_for_rc("1P")
    ls_from_1p = base.get_ls_exceptions_for_rc("1P")

    base.lz_exceptions_by_rc = {base.ctrl_rc_id: list(lz_from_1p)}
    base.ls_exceptions_by_rc = {base.ctrl_rc_id: list(ls_from_1p)}

    return base


# --- Модель с контролируемой 1-7SP ---


def get_station_model_17_ctrl() -> StationModel1P:
    """
    Модель участка с контролируемой РЦ 1-7SP.
    Используется в сценариях v4/v12 для 1-7СП.
    """
    base = get_station_model_1p()

    base.ctrl_rc_id = "1-7SP"
    base.prev_candidates = []   
    base.next_candidates = ["1P"]      

    lz_from_1p = base.get_lz_exceptions_for_rc("1P")
    ls_from_1p = base.get_ls_exceptions_for_rc("1P")

    base.lz_exceptions_by_rc = {base.ctrl_rc_id: list(lz_from_1p)}
    base.ls_exceptions_by_rc = {base.ctrl_rc_id: list(ls_from_1p)}

    return base


# --- Утилиты для интерпретации Uni_State_ID по РЦ и стрелкам ---


def rc_is_free(uni_state_id: int) -> bool:
    """
    РЦ свободна: Uni_State_ID из списка {3, 4, 5}.
    """
    return uni_state_id in (3, 4, 5)


def rc_is_occupied(uni_state_id: int) -> bool:
    """
    РЦ занята: Uni_State_ID из списка {6, 7, 8}.
    """
    return uni_state_id in (6, 7, 8)


def rc_is_locked(uni_state_id: int) -> bool:
    """
    РЦ замкнута (З=1): Uni_State_ID из списка {4, 5, 7, 8}.
    4 — свободна, замкнута;
    5 — свободна, замкнута, искусственно размыкается;
    7 — занята, замкнута;
    8 — занята, замкнута, искусственно размыкается.
    """
    return uni_state_id in (4, 5, 7, 8)


def rc_no_control(uni_state_id: int) -> bool:
    """
    Простейшая трактовка отсутствия контроля/непредусмотренного состояния.
    При необходимости дополним списком кодов.
    """
    return uni_state_id in (0, 1, 2, 100)


def sw_is_plus(uni_state_id: int) -> bool:
    """
    Стрелка в плюсовом положении (ПК): Uni_State_ID 3–8 для Uni_Type_ID=2.
    """
    return uni_state_id in (3, 4, 5, 6, 7, 8)


def sw_is_minus(uni_state_id: int) -> bool:
    """
    Стрелка в минусовом положении (МК): Uni_State_ID 9–14.
    """
    return uni_state_id in (9, 10, 11, 12, 13, 14)


def sw_lost_control(uni_state_id: int) -> bool:
    """
    Потеря контроля стрелки: Uni_State_ID 15–20.
    """
    return uni_state_id in (15, 16, 17, 18, 19, 20)


# --- Утилиты для интерпретации Uni_State_ID светофора ---


def signal_is_open(uni_state_id: int) -> bool:
    """
    Светофор открыт для поездного движения (зелёные / разрешающие показания).
    Для маневровых (М1) используем signal_is_shunting.
    """
    return uni_state_id in {
        3,   # один зелёный
        4,   # зелёный мигающий
        5,   # один жёлтый
        6,   # один жёлтый мигающий
        7,   # два жёлтых
        8,   # два жёлтых, верхний мигает
        9,   # три жёлтых
        10,  # зелёный мигающий + жёлтый
        11,  # зелёный + белый
        12,  # жёлтый + белый
        13,  # два зелёных
        14,  # жёлтый мигающий + белый
        16,  # один белый (маневровое на маршрутном)
        17,  # два белых (ускоренные маневры)
        18,  # белый мигающий + красный (пригласительный)
        20,  # зелёный + жёлтый
        22,  # зелёный + жёлтый
        23,  # зелёный мигающий + жёлтый + белый
        24,  # белый мигающий + отказ
    }


def signal_is_shunting(uni_state_id: int) -> bool:
    """
    Маневровое разрешение (белые огни / ускоренные маневры / комбинированные).
    """
    return uni_state_id in {
        4,
        5,
    }


def signal_has_invitation(uni_state_id: int) -> bool:
    """
    Пригласительный сигнал (мигающий белый, с красным/отказом/комбинацией).
    """
    return uni_state_id in {
        18,
        24,
        23,
    }


def signal_is_closed(uni_state_id: int) -> bool:
    """
    Светофор закрыт: запрещающее показание для поездного движения.
    """
    return uni_state_id == 15


def signal_failure(uni_state_id: int) -> bool:
    """
    Отказ на светофоре (нет огня / некорректное состояние).
    """
    return uni_state_id in {
        19,
        21,
        6,
    }


def shunting_signal_is_closed(uni_state_id: int) -> bool:
    """
    Маневровый светофор закрыт:
      - 3: синий (запрет маневров),
      - 7: красный (запрещающее поездное на маневровом).
    """
    return uni_state_id in {3, 7}
