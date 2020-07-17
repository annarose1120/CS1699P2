from driver import preprocess, hasAccess
import time

trials = 50 # number of trials to perform for each measurement
testFiles = ["t1.json", "t2.json", "t3.json", "t4.json", "t5.json"] # policy files to time

for file in testFiles:
    print("{}\n------------".format(file))

    total = 0
    #time the preprocess function trials # of times, calculate the average
    for a in range(0,trials):
        start = time.time()
        permissions, socialNetwork, nodes, resources = preprocess(file)
        end = time.time()
        total = total + (end - start)
    avg = total/trials
    print("Average processing time: {}".format(avg))

    #time the query trials # of times, calculate the average
    total = 0
    for a in range(0, trials):
        start = time.time()
        hasAccess("file.txt", "Marie", "read", socialNetwork, resources, nodes)
        end = time.time()
        total = total + (end - start)
    avg = total/trials
    print("Average query time: {}\n".format(avg))
