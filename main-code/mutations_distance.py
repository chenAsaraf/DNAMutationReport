import edit_distance
import random
import math
from Bio import pairwise2
from enum import Enum

"""
This modulo is based on the 'edit_distance' library, that implements the Levenshtein distance.
Informally, the Levenshtein distance between two words is the minimum number of single-character edits
(insertions, deletions or substitutions) required to change one word into the other (wikipedia)
To be noted: The 'edit_distance' library implementation could likely be optimized to be faster
within Python. And could probably be much faster if implemented in C.

We used the following documentation:
https://docs.python.org/2/library/difflib.html
"""
INSERTS = 0
REPLACES = 1
DELETES = 2

class PointMutation:

    def __init__(self, output_prefix):
        self.output_prefix = output_prefix
        # self.counters = [0, 0, 0, 0]  # counters for each mutation types: inserts, replaces, deletes and matches
        self.counterOfComparisons = 0  # number of compared contigs
        self.sumOfLengths = 0  # sum lengths of all the compared contigs (for avg)
        # the keys for the Dictionary of inserts and deletes:
        bases = ('A', 'C', 'G', 'T')
        # the keys for the Dictionary of replaces
        replace = ('AC', 'AG', 'AT', 'CA', 'CG', 'CT', 'GA', 'GC', 'GT', 'TA', 'TC', 'TG')
        # set all the values in the Dictionary to 0
        self.inserts = dict.fromkeys(bases, 0)
        self.deletes = dict.fromkeys(bases, 0)
        self.replaces = dict.fromkeys(replace, 0)

    def editDistance(self, healthy, tumor):
        errors_precent = math.ceil(len(tumor)/10)  # 10% of mistakes
        # The first string (i.e 'a') is the one that is compared to the second.
        # The second string (i.e 'b') does not change.
        sequence_match = edit_distance.SequenceMatcher(a=healthy, b=tumor)
        distance = sequence_match.distance()  # distance between the contigs
        matches = sequence_match.matches()  # the matches (the same chars) between the contigs

        if distance < errors_precent:
            self.counterOfComparisons += 1
            self.sumOfLengths += len(tumor)
            # counters of: inserts, replaces and deletes
            counters_for_mutations = [0, 0, 0]
            # Strings for later printed samples:
            TheInserts = "Actual inserts: "
            TheReplaces = "Actual replaces: "
            TheDeletes = "Actual deletes: "

            for opcode in sequence_match.get_opcodes():  # Return list of 5-tuples describing how to turn a into b
                if opcode[0] == "insert":
                    counters_for_mutations[INSERTS] += 1
                    inserted_char = tumor[opcode[3]:opcode[4]]
                    # Add the char that we insert to the tumor contig
                    TheInserts = TheInserts + inserted_char + ", "
                    # Increase the char-entry in the dictionary
                    self.inserts[inserted_char] += 1
                if opcode[0] == "replace":
                    counters_for_mutations[REPLACES] += 1
                    replaced_from = healthy[opcode[1]:opcode[2]]
                    replaced_to = tumor[opcode[3]:opcode[4]]
                    TheReplaces = TheReplaces + replaced_from + "->" + replaced_to + ", "
                    # Increase the chars-entry in the dictionary
                    self.replaces[replaced_from + replaced_to] += 1
                if opcode[0] == "delete":
                    counters_for_mutations[DELETES] += 1
                    deleted_char = healthy[opcode[1]:opcode[2]]
                    TheDeletes = TheDeletes + deleted_char + ", "
                    # Increase the chars-entry in the dictionary
                    self.deletes[deleted_char] += 1
            if random.choice(range(1, 101)) > 90 and distance > 0:  # Take 1/10 from the compared contigs to the sampling report in term that there are at least 1 mutation between them
                f = open(self.output_prefix + ".txt", "a")  # The sampling report
                f.write("\n============================================================================\n")
                alignment = pairwise2.align.globalxx(tumor, healthy)
                f.write(pairwise2.format_alignment(*alignment[0]))
                # f.write("Edit Distance: " + str(distance) + "\n")
                # f.write("The matches of this contigs: " + str(sequence_match.matches()) + "\n")
                # For each mutation type, check if there are mutations like this type and add to the sampling report with the mutations themselves
                if counters_for_mutations[INSERTS] > 0:
                    f.write("Inserts Amount: " + str(counters_for_mutations[INSERTS]) + ". " + TheInserts + "\n")
                else:
                    f.write("Inserts Amount: " + str(counters_for_mutations[INSERTS]) + ". \n")
                if counters_for_mutations[REPLACES] > 0:
                    f.write("Replaces Amount: " + str(counters_for_mutations[REPLACES]) + ". " + TheReplaces + "\n")
                else:
                    f.write("Replaces Amount: " + str(counters_for_mutations[REPLACES]) + ". \n")
                if counters_for_mutations[DELETES] > 0:
                    f.write("Deletes Amount: " + str(counters_for_mutations[DELETES]) + ". " + TheDeletes + "\n")
                else:
                    f.write("Deletes Amount: " + str(counters_for_mutations[DELETES]) + ". \n")
                f.close()
            self.counters[0] += counters_for_mutations[0]  # Add the part of inserts in the contig
            self.counters[1] += counters_for_mutations[1]  # Add the part of replaces in the contig
            self.counters[2] += counters_for_mutations[2]  # Add the part of deletes from the contig
            self.counters[3] += matches  # Add the part of matches between the contigs
