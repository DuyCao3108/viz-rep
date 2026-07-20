import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter

x = ["A", "B", "C"]
y = [0.12, 0.045, 0.302]

fig, ax = plt.subplots()
bars = ax.bar(x, y)

ax.yaxis.set_major_formatter(FuncFormatter(lambda v, pos: f"{v*100:.0f}%"))
ax.bar_label(bars, labels=[f"{v*100:.0f}%" for v in y])

plt.show()
