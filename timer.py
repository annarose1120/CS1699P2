from driver import preprocess, hasAccess
import time
trials = 5
testFiles = ["temp.json"]

for a in range(0,trials):
    start = time.time()
    permissions, socialNetwork, nodes, resources = preprocess(testFiles[0])
    end = time.time()
    print("preprocess time{}".format(end - start))

for a in range(0, trials):
    start = time.time()
    hasAccess("photos", "Veronica", "read", socialNetwork, resources, nodes)
    end = time.time()
    print("query time{}".format(end - start))
