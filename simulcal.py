"""
This program is free software: you can redistribute it and/or modify it under
the terms of the GNU General Public License as published by the Free Software
Foundation, either version 3 of the License, or (at your option) any later
version.
This program is distributed in the hope that it will be useful, but WITHOUT
ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.
You should have received a copy of the GNU General Public License along with
this program. If not, see <https://www.gnu.org/licenses/>.
"""

# COPYRIGHT SECTION
__author__ = "Diego Carvalho"
__copyright__ = "Copyright 2024"
__credits__ = ["Diego Carvalho"]
__license__ = "GPL"
__version__ = "0.0.2"
__maintainer__ = "Diego Carvalho"
__email__ = "diego.carvalho@cefet-rj.br"
__status__ = "development"

from collections import defaultdict

import streamlit as st
import pandas as pd

import numpy as np

import calplot
from matplotlib.colors import ListedColormap

import copy

from datetime import datetime, timedelta
from enum import Enum


class DAY_TYPE(Enum):
    SUNDAY = 0
    WORKDAY = 1
    VACATION = 2
    PF = 3
    PINI = 4
    PFIM = 5
    GREVE = 6


calcol = ListedColormap(
    ["blue", "#DDD", "#618CCF", "yellow", "green", "#F1C196", "red"]
)
csfont = {"fontname": "Avenir"}
hfont = {"fontname": "Avenir"}
workdays = [1, 3, 4, 5]


def day_color(day: datetime, offset_ferias) -> tuple[int, int]:
    if day.weekday() == 6:
        return DAY_TYPE.SUNDAY.value, 0

    if day.year == 2024:

        if (day.month == 5 and day.day >= 2) or (day.month == 6 and day.day <= 23):
            return DAY_TYPE.GREVE.value, 0

        if (day.month == 2 and day.day == 21) or (day.month == 7 and day.day == 31):
            return DAY_TYPE.PINI.value, 1

        if (day.month == 6 and day.day == 26) or (day.month == 12 and day.day == 7):
            return DAY_TYPE.PFIM.value, 1

        if day.month == 6 and day.day >= 27 and day.day <= 29:
            return DAY_TYPE.PF.value, 0
        if day.month == 7 and day.day >= 1 and day.day <= 3:
            return DAY_TYPE.PF.value, 0
        if day.month == 12 and day.day >= 9 and day.day <= 14:
            return DAY_TYPE.PF.value, 0

        val = DAY_TYPE.VACATION.value
        if day.month == 1 and day.day <= 28:
            return val, 0
        if day.month == 2 and day.day >= 9 and day.day <= 18:
            return val, 0
        if day.month == 3 and day.day >= 29 and day.day <= 31:
            return val, 0
        if day.month == 4 and day.day >= 22 and day.day <= 23:
            return val, 0
        if day.month == 5 and day.day == 1:
            return val, 0
        if day.month == 5 and day.day >= 30 and day.day <= 31:
            return val, 0
        if day.month == 7 and day.day >= 8 and day.day <= 28:
            return val, 0
        if day.month == 9 and day.day == 7:
            return val, 0
        if (day.month == 10 and day.day == 12) or (day.month == 10 and day.day == 28):
            return val, 0
        if day.month == 11 and (day.day == 2 or day.day == 20):
            return val, 0
        if day.month == 11 and day.day >= 15 and day.day <= 16:
            return val, 0
        if day.month == 12 and day.day == 25:
            return val, 0

    if day.year == 2025:
        val = DAY_TYPE.VACATION.value
        start_date = datetime(2025, 1, 1) + timedelta(offset_ferias)
        period = [start_date + timedelta(n) for n in range(28)]
        if day in period:
            return val, 0

        # Carnaval
        if day.month == 2 and day.day == 28:
            return val, 0
        if day.month == 3 and day.day >= 1 and day.day <= 5:
            return val, 0

        if day.month == 5 and day.day == 1:
            return val, 0
        if day.month == 11 and (day.day == 2 or day.day == 15):
            return val, 0
        if day.month == 12 and day.day == 25:
            return val, 0

    return DAY_TYPE.WORKDAY.value, 1


def create_csv(offset_ferias):
    delta = timedelta(days=1)
    day = datetime(year=2024, month=1, day=1)
    num_ranges = 366 + 365 + 365
    num_day = 0
    greve_day = 0

    with open("cal.csv", "w") as f:
        f.write("ds,value\n")
        for _ in range(num_ranges):
            day_str = day.strftime("%Y-%m-%d")

            day_type, count_day = day_color(day, offset_ferias)

            num_day += count_day

            if day_type == 4:
                print(f"Início de Semestre = {day_str}, Contagem = {num_day}")
                num_day = 1

            if day_type == 5:
                print(f"   Fim de Semestre = {day_str}, Contagem = {num_day}")
                num_day = 0

            if day_type == 6:
                greve_day += 1

            f.write(f"{day_str},{day_type}\n")
            day += delta

    print(f"Dias de aula em greve: {greve_day}.")


def st_init() -> None:
    st.set_page_config(layout="wide")


def main():
    st_init()

    offset_ferias = st.slider("Dias de Offset nas férias", 0, 60, 0)

    create_csv(offset_ferias)

    df = pd.read_csv("cal.csv")
    df.ds = pd.to_datetime(df.ds)
    events = pd.Series(df.value.values, index=pd.DatetimeIndex(df.ds))
    fig, ax = calplot.calplot(
        events,
        cmap=calcol,
        colorbar=False,
        suptitle="Calendário Cefet/RJ original com a Greve",
        monthlabels=[
            "Jan",
            "Fev",
            "Mar",
            "Abr",
            "Mai",
            "Jun",
            "Jul",
            "Ago",
            "Set",
            "Out",
            "Nov",
            "Dec",
        ],
        daylabels=["Seg", "Ter", "Qua", "Qui", "Sex", "Sab", "Dom"],
        suptitle_kws=csfont,
    )

    fig.set_dpi(300)
    fig.set_size_inches((15, 4.8))
    fig.savefig("CAL-ORIG.png")
    st.pyplot(fig, clear_figure=None, use_container_width=True)

    offset = st.slider("Dias de Offset", 0, 30, 0)

    source = list(df.value.values)
    dest = list(df.value.values)

    pos = 175

    scount = source.count(6)
    n_greve = st.slider(
        f"Dias de reposição ({source.count(6)} dias de greve)", 0, 60, scount
    )

    qnt = n_greve + offset

    move = 1

    for _ in range(qnt):
        i = pos
        while i <= 600:
            if source[i] in workdays:
                for k in range(1, 40):
                    if dest[i + k] in workdays:
                        move = k
                        break
            dest[i + move] = source[i]
            i += move
        source = copy.deepcopy(dest)

    events2 = pd.Series(dest, index=pd.DatetimeIndex(df.ds))
    fig2, ax = calplot.calplot(
        events2,
        cmap=calcol,
        colorbar=False,
        suptitle="Calendário Cefet/RJ reposição",
        monthlabels=[
            "Jan",
            "Fev",
            "Mar",
            "Abr",
            "Mai",
            "Jun",
            "Jul",
            "Ago",
            "Set",
            "Out",
            "Nov",
            "Dec",
        ],
        daylabels=["Seg", "Ter", "Qua", "Qui", "Sex", "Sab", "Dom"],
        suptitle_kws=csfont,
    )

    fig2.set_dpi(300)
    fig2.set_size_inches((15, 4.8))
    st.pyplot(fig2, clear_figure=None, use_container_width=True)


if __name__ == "__main__":
    main()
