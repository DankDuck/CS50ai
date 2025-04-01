import csv
import itertools
import sys

PROBS = {

    # Unconditional probabilities for having gene
    "gene": {
        2: 0.01,
        1: 0.03,
        0: 0.96
    },

    "trait": {

        # Probability of trait given two copies of gene
        2: {
            True: 0.65,
            False: 0.35
        },

        # Probability of trait given one copy of gene
        1: {
            True: 0.56,
            False: 0.44
        },

        # Probability of trait given no gene
        0: {
            True: 0.01,
            False: 0.99
        }
    },

    # Mutation probability
    "mutation": 0.01
}


def main():

    # Check for proper usage
    if len(sys.argv) != 2:
        sys.exit("Usage: python heredity.py data.csv")
    people = load_data(sys.argv[1])

    # Keep track of gene and trait probabilities for each person
    probabilities = {
        person: {
            "gene": {
                2: 0,
                1: 0,
                0: 0
            },
            "trait": {
                True: 0,
                False: 0
            }
        }
        for person in people
    }

    # Loop over all sets of people who might have the trait
    names = set(people)
    for have_trait in powerset(names):

        # Check if current set of people violates known information
        fails_evidence = any(
            (people[person]["trait"] is not None and
             people[person]["trait"] != (person in have_trait))
            for person in names
        )
        if fails_evidence:
            continue

        # Loop over all sets of people who might have the gene
        for one_gene in powerset(names):
            for two_genes in powerset(names - one_gene):

                # Update probabilities with new joint probability
                p = joint_probability(people, one_gene, two_genes, have_trait)
                update(probabilities, one_gene, two_genes, have_trait, p)

    # Ensure probabilities sum to 1
    normalize(probabilities)

    # Print results
    for person in people:
        print(f"{person}:")
        for field in probabilities[person]:
            print(f"  {field.capitalize()}:")
            for value in probabilities[person][field]:
                p = probabilities[person][field][value]
                print(f"    {value}: {p:.4f}")


def load_data(filename):
    """
    Load gene and trait data from a file into a dictionary.
    File assumed to be a CSV containing fields name, mother, father, trait.
    mother, father must both be blank, or both be valid names in the CSV.
    trait should be 0 or 1 if trait is known, blank otherwise.
    """
    data = dict()
    with open(filename) as f:
        reader = csv.DictReader(f)
        for row in reader:
            name = row["name"]
            data[name] = {
                "name": name,
                "mother": row["mother"] or None,
                "father": row["father"] or None,
                "trait": (True if row["trait"] == "1" else
                          False if row["trait"] == "0" else None)
            }
    return data


def powerset(s):
    """
    Return a list of all possible subsets of set s.
    """
    s = list(s)
    return [
        set(s) for s in itertools.chain.from_iterable(
            itertools.combinations(s, r) for r in range(len(s) + 1)
        )
    ]


def joint_probability(people, one_gene, two_genes, have_trait):
    """
    Compute and return a joint probability.

    The probability returned should be the probability that
        * everyone in set `one_gene` has one copy of the gene, and
        * everyone in set `two_genes` has two copies of the gene, and
        * everyone not in `one_gene` or `two_gene` does not have the gene, and
        * everyone in set `have_trait` has the trait, and
        * everyone not in set` have_trait` does not have the trait.
    """
    # Create overall probabilities list
    prob = []
    final_joint = 1
    for person, data in people.items():
        # If parents exit
        if data["mother"] != None and data["father"] != None:
            child_gene_prob = 0
            # Find child's gene info
            gene_num, gene_prob = get_gene_prob(data["name"], one_gene, two_genes)
            # Find each parents' gene info
            mom_gene_num, mom_gene_prob = get_gene_prob(data["mother"], one_gene, two_genes)
            dad_gene_num, dad_gene_prob = get_gene_prob(data["father"], one_gene, two_genes)

            # Get inheritance probabilites from each parent
            mom_inheritance = get_inheritance(mom_gene_num)
            dad_inheritance = get_inheritance(dad_gene_num)

            # Calculate diff probabilities of child's genes
            if gene_num == 0:
                child_gene_prob = 1-mom_inheritance * 1-dad_inheritance
            elif gene_num == 1:
                # add up probabilites when either dad only passes down gene or mom only passes down gene
                child_gene_prob = (1-mom_inheritance) * dad_inheritance + mom_inheritance * (1-dad_inheritance)
            else:
                child_gene_prob = mom_inheritance * dad_inheritance

            # Get trait probability and add it 
            child_trait_prob = get_trait_prob(data["name"], gene_num, have_trait)
            prob.append(child_gene_prob * child_trait_prob)           
        # No parents
        else:
            # Get gene num and prob and trait prob
            gene_num, gene_prob = get_gene_prob(data["name"], one_gene, two_genes)
            trait_prob = get_trait_prob(data["name"], gene_num, have_trait)
            # Add joint prob to final joint probabilities
            prob.append(gene_prob * trait_prob)
    # Multiply each probability in prob table and then return it
    for x in prob:
        final_joint *= x
    return final_joint
 
# Return num of genes and prob as tuple based on if they are in the arguments
def get_gene_prob(person, one_gene, two_genes):
    gene_prob = 0
    gene_num = 0

    if person in one_gene:
        gene_num = 1
        gene_prob = PROBS["gene"][1]
    elif person in two_genes:
        gene_num = 2
        gene_prob = PROBS["gene"][2]
    else:
        gene_prob = PROBS["gene"][0]
    
    return (gene_num, gene_prob)

# Return trait prob based on if they are in the arguments
def get_trait_prob(person, gene_num, have_trait):
    trait_prob = 0
    if person in have_trait:
        trait_prob = PROBS["trait"][gene_num][True]
    else:
        trait_prob = PROBS["trait"][gene_num][False]

    return trait_prob

# Return inheritance chance based on the parent's number of genes
def get_inheritance(gene_num):
    inheritance_chance = 0
    if gene_num == 0:
        inheritance_chance = PROBS["mutation"]
    elif gene_num == 1:
        inheritance_chance = 0.5 * PROBS["mutation"]
    else:
        inheritance_chance = 1-PROBS["mutation"]
    return inheritance_chance

# Update each probability by adding p
def update(probabilities, one_gene, two_genes, have_trait, p):
    """
    Add to `probabilities` a new joint probability `p`.
    Each person should have their "gene" and "trait" distributions updated.
    Which value for each distribution is updated depends on whether
    the person is in `have_gene` and `have_trait`, respectively.
    """
    for person, data in probabilities.items():
        if person in one_gene:
            data["gene"][1] += p
        elif person in two_genes:
            data["gene"][2] += p
        else:
            data["gene"][0] += p

        if person in have_trait:
            data["trait"][True] += p
        else:
            data["trait"][False] += p

# Make sure probabilities add up to 1
def normalize(probabilities):
    """
    Update `probabilities` such that each probability distribution
    is normalized (i.e., sums to 1, with relative proportions the same).
    """
    for person, data in probabilities.items():
        norm_gene_factor = 1 / (data["gene"][0] + data["gene"][1] + data["gene"][2])
        data["gene"][0] *= norm_gene_factor
        data["gene"][1] *= norm_gene_factor
        data["gene"][2] *= norm_gene_factor

        norm_trait_factor = 1 / (data["trait"][True] + data["trait"][False])
        data["trait"][True] *= norm_trait_factor
        data["trait"][False] *= norm_trait_factor


if __name__ == "__main__":
    main()
