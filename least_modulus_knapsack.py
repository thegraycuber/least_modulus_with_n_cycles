import incomplete_knapsack as ik
import math


def item_input(file_name):
    with open(file_name, encoding="utf-8", mode="r") as f:
        lines = f.readlines()

    data = []
    for x in lines:
        line = x.split(",")
        data.append(
            ik.Item(
                line[0],
                int(line[1].replace("\n", "")),
                -math.log(float(line[0])),
                len(data),
            )
        )

    return data


# A379423
item_list = item_input("A379423_factors.csv")
sequence, item_list = ik.incomplete_knapsack(
    item_list, item_list[-1].cost, 1, -1, 2500, True
)
# ik.sequence_output(sequence, "A379423_shorthand.csv", -1)
ik.sequence_to_explicit(sequence, item_list, "A379423.csv", 5000)
# ik.sequence_to_explicit(sequence, item_list, "b379423.txt", 1000, 1, " ") #create b file for OEIS

# A379424
item_list = item_input("A379424_factors.csv")
sequence, item_list = ik.incomplete_knapsack(
    item_list, item_list[-1].cost, 1, -1, 2500, True
)
# ik.sequence_output(sequence, "A379424_shorthand.csv", -1)
ik.sequence_to_explicit(sequence, item_list, "A379424.csv", 2500)
# ik.sequence_to_explicit(sequence, item_list, "b379424.txt", 500, 1, " ") #create b file for OEIS
