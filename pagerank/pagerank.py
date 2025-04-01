import os
import random
import re
import sys

DAMPING = 0.85
SAMPLES = 10000


def main():
    if len(sys.argv) != 2:
        sys.exit("Usage: python pagerank.py corpus")
    corpus = crawl(sys.argv[1])
    ranks = sample_pagerank(corpus, DAMPING, SAMPLES)
    print(f"PageRank Results from Sampling (n = {SAMPLES})")
    for page in sorted(ranks):
        print(f"  {page}: {ranks[page]:.4f}")
    ranks = iterate_pagerank(corpus, DAMPING)
    print(f"PageRank Results from Iteration")
    for page in sorted(ranks):
        print(f"  {page}: {ranks[page]:.4f}")


def crawl(directory):
    """
    Parse a directory of HTML pages and check for links to other pages.
    Return a dictionary where each key is a page, and values are
    a list of all other pages in the corpus that are linked to by the page.
    """
    pages = dict()

    # Extract all links from HTML files
    for filename in os.listdir(directory):
        if not filename.endswith(".html"):
            continue
        with open(os.path.join(directory, filename)) as f:
            contents = f.read()
            links = re.findall(r"<a\s+(?:[^>]*?)href=\"([^\"]*)\"", contents)
            pages[filename] = set(links) - {filename}

    # Only include links to other pages in the corpus
    for filename in pages:
        pages[filename] = set(
            link for link in pages[filename]
            if link in pages
        )

    return pages


def transition_model(corpus, page, damping_factor):
    """
    Return a probability distribution over which page to visit next,
    given a current page.

    With probability `damping_factor`, choose a link at random
    linked to by `page`. With probability `1 - damping_factor`, choose
    a link at random chosen from all pages in the corpus.
    """
    numOfPages = len(corpus)
    links = corpus[page]
    distribution = dict()
    random_page_prob = (1-damping_factor)/numOfPages

    # If page links to other pages, calculate probability of those and then add probability of going to random page
    if links:
        for pg in corpus:
            if pg in links:
                distribution[pg] = damping_factor / len(links)
                distribution[pg] += random_page_prob
            else:
                distribution[pg] = random_page_prob
    # Else if no links its equally likely to go to all pages
    else:
        for pg in corpus:
            distribution[pg] = 1 / numOfPages
    
    return distribution


def sample_pagerank(corpus, damping_factor, n):
    """
    Return PageRank values for each page by sampling `n` pages
    according to transition model, starting with a page at random.

    Return a dictionary where keys are page names, and values are
    their estimated PageRank value (a value between 0 and 1). All
    PageRank values should sum to 1.
    """
    distributions = dict()
    for page in corpus:
        distributions[page] = 0

    new_page = random.choice(list(corpus.keys()))
    distributions[new_page] = 1 

    # Loop for each sample n
    for i in range(n-1):
        page_probs = transition_model(corpus, new_page, damping_factor)
        # Separate pages and their probabilities into two lists
        pages = list()
        probabilities = list()

        for key, value in page_probs.items():
            pages.append(key)
            probabilities.append(value)
        
        # Get a random page from possibilities using probabilities as weighted (using percentages)
        new_page = random.choices(pages, probabilities)[0]
        distributions[new_page] += 1
    
    for page,distribution in distributions.items():
        distributions[page] = distribution / n

    return distributions


def iterate_pagerank(corpus, damping_factor):
    """
    Return PageRank values for each page by iteratively updating
    PageRank values until convergence.

    Return a dictionary where keys are page names, and values are
    their estimated PageRank value (a value between 0 and 1). All
    PageRank values should sum to 1.
    """
    pageranks = dict()
    page_num = len(corpus)

    # Set a default page rank for each page
    for page in corpus:
        pageranks[page] = 1 / page_num

    # Loop until changes are minimal (<.001)
    while True:
        count = 0

        # For each page, use iterative formula to calculate pagerank
        for page in corpus.keys():
            new_pagerank = (1 - damping_factor)/page_num
            sigma = 0

            for other_page, links in corpus.items():
                if page in links:
                    sigma += pageranks[other_page] / len(links)
            
            new_pagerank += sigma * damping_factor
            change = abs(pageranks[page] - new_pagerank)
            if (change < 0.001):
                count += 1
            pageranks[page] = new_pagerank
        if count > 1:
            break

    return pageranks

if __name__ == "__main__":
    main()
