import uproot
import numpy as np
import matplotlib.pyplot as plt


def toy_distribution(noncentral, multiplier, offset, num_events):
    return np.random.noncentral_chisquare(5, noncentral, num_events)*multiplier + offset


def toy_weights(total_yield, num_events):
    avg = total_yield / float(num_events)
    weights = np.random.normal(avg, avg*0.1, num_events)
    # re-normalize to make sure sum of weights exactly matches avg
    weights *= total_yield / np.sum(weights)
    return weights


def get_samples(num_events):
    dist_s1 = toy_distribution(10, 12, 350, num_events)
    dist_s2 = toy_distribution(25, 10, 500, num_events)
    dist_b  = toy_distribution(10, 25, 0, num_events)
    return [dist_s1, dist_s2, dist_b]


def get_weights(yield_s1, yield_s2, yield_b, num_events):
    w_s1 = toy_weights(yield_s1, num_events)
    w_s2 = toy_weights(yield_s2, num_events)
    w_b  = toy_weights(yield_b, num_events)
    return [w_s1, w_s2, w_b]


def create_pseudodata(yield_s1, yield_s2, yield_b):
    # create a dataset with some slightly different composition
    scale_s1 = 0.7
    scale_s2 = 1.3
    scale_b = 1.05
    dist_s1 = toy_distribution(10, 12, 350, int(yield_s1*scale_s1))
    dist_s2 = toy_distribution(25, 10, 500, int(yield_s2*scale_s2))
    dist_b  = toy_distribution(10, 25, 0, int(yield_b*scale_b))
    pseudodata = np.hstack((dist_s1, dist_s2, dist_b))
    np.random.shuffle(pseudodata)
    return pseudodata


def create_file(file_name, distributions, weights, labels):
    with uproot.recreate(file_name) as f:
        # write the predicted processes
        for i, label in enumerate(labels):
            f[label] = uproot.newtree({"jet_pt": "float64",
                                        "weight": "float64"})
            f[label].extend({"jet_pt": distributions[i],
                             "weight": weights[i]})


def create_file_pseudodata(file_name, pseudodata):
    with uproot.recreate(file_name) as f:
        # write pseudodata
        f["pseudodata"] = uproot.newtree({"jet_pt": "float64"})
        f["pseudodata"].extend({"jet_pt": pseudodata})


def read_file(file_name):
    distributions = []
    weights = []
    labels = []
    with uproot.open(file_name) as f:
        all_trees = f.allkeys(filterclass=lambda cls: issubclass(cls, uproot.tree.TTreeMethods))
        for tree in all_trees:
            distributions.append(f[tree].array("jet_pt"))
            weights.append(f[tree].array("weight"))
            labels.append(tree)
    return distributions, weights, labels


def read_file_pseudodata(file_name):
    with uproot.open(file_name) as f:
        distribution = f["pseudodata"].array("jet_pt")
    return distribution


def plot_distributions(data, weights, labels, pseudodata, bins):
    bin_width_str = str(int(bins[1] - bins[0]))

    #labels = [l.split('\'')[1] for l in labels]
    yield_each = [str(round(np.sum(w),1)) for w in weights]
    labels = [l.decode().split(";")[0] for l in labels]

    # plot normalized distributions
    for i in reversed(range(len(data))):
        plt.hist(data[i], weights=weights[i], bins=bins, label=labels[i],
                 histtype="step", density=True)
    plt.legend(frameon=False)
    plt.xlabel(r"jet $p_T$ [GeV]")
    plt.ylabel("normalized")
    plt.savefig("normalized.pdf")

    # plot stack
    plt.clf()
    labels_with_yield = [labels[i] + " " + yield_each[i] for i in range(len(labels))]
    pseudodata_label = "pseudodata " + str(len(pseudodata))
    plt.hist(data[::-1], weights=weights[::-1], bins=bins,
             label=labels_with_yield[::-1],
             histtype="stepfilled", stacked=True)
    plt.hist(pseudodata, bins=bins, label=pseudodata_label,
             histtype="step", color="k")
    plt.legend(frameon=False)
    plt.xlabel(r"jet $p_T$ [GeV]")
    plt.ylabel("events / " + bin_width_str + " GeV")
    plt.savefig("stacked.pdf")


if __name__ == '__main__':
    # configuration
    num_events = 25000
    yield_s1   = 1250
    yield_s2   = 2115
    yield_b    = 12740
    labels     = ["signal_1", "signal_2", "background"] # names of prcesses
    file_name  = "prediction.root"
    file_name_pseudodata  = "data.root"

    np.random.seed(0)

    # distributions for three processes
    distributions  = get_samples(num_events)

    # corresponding weights
    weights = get_weights(yield_s1, yield_s2, yield_b, num_events)

    # create a pseudodataset
    pseudodata = create_pseudodata(yield_s1, yield_s2, yield_b)

    # write it all to a file
    create_file(file_name, distributions, weights, labels)
    create_file_pseudodata(file_name_pseudodata, pseudodata)

    # read the files again
    d_read, w_read, l_read = read_file(file_name)
    pd_read = read_file_pseudodata(file_name_pseudodata)

    # compare predictions from before/after reading
    np.testing.assert_allclose(d_read, distributions)
    np.testing.assert_allclose(w_read, weights)
    np.testing.assert_allclose(pd_read, pseudodata)

    # visualize results
    bins = np.linspace(0, 1200, 24+1)
    plot_distributions(d_read, w_read, l_read, pseudodata, bins)
