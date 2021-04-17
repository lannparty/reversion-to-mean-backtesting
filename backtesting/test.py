import matplotlib.pyplot as plt

places = ["A", "B", "C", "D", "E", "F", "G", "H", "I", "J"]
literacy_rate = [100, 98, 90, 85, 75, 50, 30, 45, 65, 70]
female_literacy = [95, 100, 50, 60, 85, 80, 75, 99, 70, 30]

plt.xlabel("Places")
plt.ylabel("Percentage")

plt.plot(places, literacy_rate, color='blue',
		linewidth=6, label="Literacy rate")

plt.plot(places, female_literacy, color='fuchsia',
		linewidth=4, label="Female Literacy rate")

plt.legend(loc='lower left', ncol=1)
plt.show()
