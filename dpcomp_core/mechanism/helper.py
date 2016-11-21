"""Helper functions for Super MWEM"""
import numpy


def sensitivity(workload):
    ''' Compute sensitivity of a collection of ndRangeUnion queries '''
    maxShape = tuple( [max(l) for l in zip(*[q.impliedShape for q in workload])] )
    array = numpy.zeros(maxShape)
    for q in workload:
        array += q.asArray(maxShape)
    return numpy.max(array)
    
def LaplaceMechParallel(x, Queries, local_eps, seed=None):
    ''' Laplace mechanism; return list of noisy query answers '''
    numpy.random.seed(seed)
    true_ans = numpy.array([q.eval(x) for q in Queries])
    sensitivity = utilities.sensitivity(Queries)
    scale = sensitivity / float(local_eps)
    return true_ans + numpy.random.laplace(scale=scale, size=len(Queries))


def exponentialMechanism(choices, scores, sensitivity, local_eps):
    """ Generic implementation of the exponential mechanism

	choices: list of items to privately select [item1, item2, ... ]
	scores: numpy array of scores: [score1, score2, ...]
	sensitivity:  sensitivity of the score function
	local_eps - privacy parameter for this mechanism

	Returns: (index-of-item, item)
	"""
    max_score = max(scores)
    dist = numpy.exp(local_eps * (scores - max_score) / (2.0 * sensitivity))
    dist = dist / sum(dist)  # normalize
    # randomly select an index in [0..len(choices)] according to distribution
    result_index = numpy.random.choice(a=len(choices), size=1, p=dist)[0]

    # TODO: there is no reason to take choices as a parameter and then return choice
    # TODO: This function only uses scores
    return result_index, choices[result_index]


def noisyMax(choices, scores, sensitivity, epsilon):
    # The following is almost equivalent to exponential mechanism with coeff 2 in numerator / sensitivity not used -- fix:

    # set the scale to 1/local_epsilon for fair comparison with julia code.
    scale = (1 * sensitivity / epsilon)
    noise = numpy.random.laplace(scale=scale, size=len(scores))  # /2560.0
    noisy_scores = scores + noise
    result_index = numpy.argmax(noisy_scores)
    return result_index, choices[result_index]

