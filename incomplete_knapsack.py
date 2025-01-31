from dataclasses import dataclass
import sys


@dataclass
class Item:
    def __init__(self, name, weight, value, index=-1):
        self.name = name
        self.weight = weight
        self.value = value
        self.cost = value / weight
        self.index = index


@dataclass
class SequenceTerm:
    def __init__(self):
        self.exists = False
        self.weight = 0
        self.value = 0
        self.consecutive_end = -1  # this denotes a block of the first k items.
        self.additional_indices = []  # this denotes indices of any items past that initial block
        # for example, if a term uses items 0, 1, 2, 3, 5, 7, and 10
        # consecutive_end = 3
        # additional_indices = [5,7,10]

    def concatenate(self, base_term, new_item):
        self.weight = base_term.weight + new_item.weight
        self.value = base_term.value + new_item.value
        self.exists = True
        if new_item.index == base_term.consecutive_end + 1:
            self.consecutive_end = new_item.index
        else:
            self.consecutive_end = base_term.consecutive_end
            self.additional_indices = base_term.additional_indices.copy() + [
                new_item.index
            ]

    def output_string(self, index, direction=1):
        return (
            str(index)
            + ","
            + str(self.value * direction)
            + ","
            + str(self.consecutive_end)
            + ","
            + ",".join([str(x) for x in self.additional_indices])
        )


def incomplete_knapsack(
    item_list,
    max_missing_cost,
    min_missing_weight,
    limit=-1,
    update_freq=1000,
    items_sorted=False,
):
    # the items need to be sorted descending by cost for the existsation efficiency
    if not items_sorted:
        item_list = sorted(item_list, key=lambda x: x.cost, reverse=True)
        for i in range(len(item_list)):
            item_list[i].index = i

    if limit == -1:
        limit = len(item_list)

    # this is used to track the minimum weight for a future item.
    # a term sequence[s] does not need existsation against sequence[s-j] if j is below this minimum
    min_found = min_missing_weight
    min_adjust = []  # each row has the form: [index of final item with weight <= w, w]
    for i in range(len(item_list) - 1, -1, -1):
        if item_list[i].weight < min_found:
            min_adjust.append([i, min_found])
            min_found = item_list[i].weight

    # create and confirm empty terms that cannot possibly be filled
    lowest_unconfirmed = min_found
    sequence = []
    for s in range(min_found):
        sequence.append(SequenceTerm())
        sequence[s].exists = True

    # the main bit
    for item in item_list[:limit]:
        if item.index % update_freq == 0:
            print("Checking item", item.index)

        for new_term in range(item.weight):
            sequence.append(SequenceTerm())

        # check each unconfirmed term with room for the new item
        s = len(sequence)
        while s > item.weight and s > lowest_unconfirmed:
            s -= 1

            # skip if the lower sequence term doesn't exist
            if not sequence[s - item.weight].exists:
                continue

            # update the term if it doesn't exist or if it is beaten
            if (not sequence[s].exists) or sequence[
                s - item.weight
            ].value + item.value > sequence[s].value:
                sequence[s].concatenate(sequence[s - item.weight], item)

        # try to confirm more terms
        for s in range(lowest_unconfirmed, len(sequence)):
            # can't confirm something that doesn't exist
            if not sequence[s].exists:
                break
            # auto confirm if it uses only a block. this is because of sort by cost. there is no possible way to beat this.
            if len(sequence[s].additional_indices) == 0:
                lowest_unconfirmed += 1
                continue

            is_confirmed = True

            for w in range(min_missing_weight, min(s + 1, 2 * min_missing_weight)):
                # if there is possibility of beaten by some missing item, then unconfirmable
                if sequence[s - w].value + max_missing_cost * w >= sequence[s].value:
                    print(
                        "Unconfirmable at term",
                        lowest_unconfirmed,
                        "Sequence",
                        sequence[s].output_string(s),
                        "Weight",
                        sequence[s - w].output_string(s - w),
                    )
                    return sequence[:lowest_unconfirmed], item_list

            for w in range(min_found, min(s + 1, 2 * min_found)):
                # if there is possibility of beaten by some included item, not confirmed yet
                if sequence[s - w].value + item.cost * w >= sequence[s].value:
                    is_confirmed = False
                    break

            if is_confirmed:
                lowest_unconfirmed += 1
            else:
                break

        # cleanup min_adjust
        if len(min_adjust) > 0 and item.index == min_adjust[-1][0]:
            min_found = min_adjust[-1][1]
            min_adjust.pop()
    print("Reached limit, with confirmed up to", lowest_unconfirmed)
    return sequence[:lowest_unconfirmed], item_list


# this assumes that the names for the items are meant to be multiplied together, which applies for all I've used so far.
def sequence_to_explicit(
    sequence, item_list, file_name, limit=-1, multiplier=1, delimiter=","
):
    sys.set_int_max_str_digits(0)
    if limit == -1:
        limit = len(sequence) - 1
    else:
        limit = min(len(sequence) - 1, limit)

    consecutive = [multiplier * int(item_list[0].name)]
    last_explicit = -1
    with open(file_name, "w", encoding="utf-8") as f:
        for s in range(limit + 1):
            while len(consecutive) <= sequence[s].consecutive_end:
                consecutive.append(
                    consecutive[-1] * int(item_list[len(consecutive)].name)
                )

            if sequence[s].consecutive_end == -1:
                explicit_term = multiplier
            else:
                explicit_term = consecutive[sequence[s].consecutive_end]
            for m in sequence[s].additional_indices:
                explicit_term *= int(item_list[m].name)

            if last_explicit > explicit_term:
                explicit_term = last_explicit
            f.write(str(s) + delimiter + str(explicit_term) + "\n")
            last_explicit = explicit_term


def sequence_output(data_output, file_name, direction):
    with open(file_name, "w", encoding="utf-8") as f:
        for d in range(len(data_output)):
            f.write(data_output[d].output_string(d, direction) + "\n")
