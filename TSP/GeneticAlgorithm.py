import matplotlib.pyplot as plt
import math
import csv
import xml.etree.ElementTree as ET
import random
import timeit

class GeneticAlgorithm:

    """This class models a Genetic Algorithm used to solve the Traveling Salesman Problem where essentially a
        Salesman has to travel to all given cities and this algorithm selects the solution that takes the least distance.

        The class works using the following steps:
        1. Convert the datafiles to a cost matrix that contains the distance of all possible cities combinations.
        2. Generate a population of possible paths modeled as genetic chromosomes and calculate their distances.
        3. Using tournament selection, select a bunch of chromosomes (possibles paths), per two chromosomes do a crossover
           forming two children and then mutate the children.
        4. Reintroduce all the children to the intial population if they are better than the initial population.
        5. Repeat this evolution cycle for as many times as required.

        """

    def __init__(self,filePath,popSize,evolutionCycles,
                 tourSize,mutatMethod,crossover_function,mutatTime=None):
        self.lengthMat = None
        self.filePath = filePath
        self.popSize = popSize
        self.costMatrix = None
        self.evolutionCycles = evolutionCycles
        self.tourSize = tourSize
        self.mutatMethod = mutatMethod
        self.crossover_function = crossover_function
        self.mutatTime = mutatTime
        if mutatMethod == 'M' and mutatTime is None:
            raise TypeError('If the mutation function is M or Multiple Swap Mutation then the mutation time cannot be blank')


    @staticmethod
    def euclid_distance(x1,y1,x2,y2):
        # calculates distance to convert location coordinates to a cost matrix
        ans = math.sqrt((x2-x1)**2 + (y2-y1)**2)
        return ans


    def xml_to_matrix(self):
        # OBSOLETE FUNCTION
        # this function takes an XML filepath and converts it into a square matrix of a given length
        # this uses solely for the problem and is not too generalized
        # parse XML data
        tree = ET.parse(self.filePath)
        root = tree.getroot()
        # need to find the maximum number of cities since it is not mentioned anywhere , we just brute force it
        all_edges = []
        for edge in root.iter('edge'):
            all_edges.append(int(edge.text))
        self.lengthMat = max(all_edges)+1

        # create a dummy matrix full of zeroes
        A = [[0 for _ in range(self.lengthMat)] for _ in range(self.lengthMat)]

        # we use tag in for loop to assign values to matrix
        i = 0
        # take the edge values
        for edge in root.iter('edge'):
            # e = edge no
            e = int(edge.text)
            # reset tag
            if i > self.lengthMat - 1:
                i = 0
            # b = edge distance/cost
            for key, value in edge.attrib.items():
                b = float(value)
            # assign value to matrix
            A[i][e] = b
            # increment tag
            i += 1

        # return the matrix containing distances
        return A


    def text_to_matrix(self):
        # function used to generate an n-by-n matrix
        # that contains the distance to travel from ith to jth city in the dataset

        # open file and get no of cites using hard coded position
        with open(self.filePath,'r') as f:
            self.lengthMat  = int(f.readlines()[2][11:])
        # gets the x and y coordinates of all the cites, assume all values are ints
        coord_matrix  = []
        with open(self.filePath,'r') as f:
            for line in f.readlines()[10:10+self.lengthMat]:
                coord_matrix.append([int(x) for x in line.split()])

        # create a dummy matrix full of zeroes
        A = [[0 for _ in range(self.lengthMat)] for _ in range(self.lengthMat)]

        # calculate the cost matrix which is essentially just the distance from city i to city j
        for i in range(self.lengthMat):
            for j in range(self.lengthMat):
                A[i][j] = self.euclid_distance(coord_matrix[i][1],coord_matrix[i][2],
                                               coord_matrix[j][1],coord_matrix[j][2])
        return A

    @staticmethod
    def generate_one_chromosome (lengthC):
        # function to create one chromosome
        numbers = random.sample(range(0, lengthC), lengthC)
        return numbers


    def generate_population(self,chromLength):
        # function that generates population of chromosomes depending on the
        # given chromosome size and population size, output as a list within lists (matrix)
        ouputP = []
        # for each individual we generate a random chromosome
        for i in range(self.popSize):
            ouputP.append(self.generate_one_chromosome(chromLength))
        return ouputP


    def fitness_func(self,inputChrom):
        # fitness function uses the cost matrix to calculate the cost from moving
        # from one city to another city for all cities in the input chromosome
        cost = 0
        # the final city
        n = len(inputChrom)-1
        for i in range(len(inputChrom)-1):
            # from city i to i+1 (the chosen city and the city after that)
            # row i in matrix starts from city i+1 and column i+1 is the distance from i to i+1
            cost += self.costMatrix[inputChrom[i]][inputChrom[i+1]]
        # after that we must loop back to our starting city
        cost += self.costMatrix[inputChrom[n]][inputChrom[0]]
        return cost


    def tournament_selection (self,population,tournaSize):
        # first we choose the chromosomes for the tournament
        tourPopulation = random.choices(population,k=tournaSize)

        # then we sort based on the fitness of the chromosomes and take the fittest one
        selection = sorted(tourPopulation,key = lambda x : self.fitness_func(x))

        return selection[0]


    @staticmethod
    def single_crossover_ordered(parentA, parentB):
        # this function does the first ordered crossover
        # size of parent A and parent B must be the same
        if len(parentA) != len(parentB):
            raise Exception('Parent A and B must be the same length')

        # choose crossover point
        lenChrom = len(parentA)
        # cross over point can't be starting or ending index of list
        crossPoint = random.randint(1,lenChrom-1)

        # childA contains a bit of A from crossover point to the end and the remaining values,
        # missing values are taken in the order of their appearance from parent B
        # child A  = Missing of A in order of Parent B + Parent A
        # child B  = Missing of B in order of Parent A + Parent B
        # the missing variables takes the difference and puts them in order
        missingA = [x for x in parentB if x not in parentA[crossPoint:lenChrom]]
        missingB = [x for x in parentA if x not in parentB[crossPoint:lenChrom]]

        # and then we do the crossover
        childA = missingA + parentA[crossPoint:lenChrom]
        childB = missingB + parentB[crossPoint:lenChrom]

        return childA,childB


    @staticmethod
    def single_crossover_with_fix(parentA, parentB):
        # same as above but with fix the missing parts
        # size of parent A and parent B must be the same
        if len(parentA) != len(parentB):
            raise Exception('Parent A and B must be the same length')
        # choose crossover point
        lenChrom = len(parentA)
        # cross over point can't be starting or ending index of list
        crossPoint = random.randint(1, lenChrom - 1)
        # and then split
        # to form children
        # child A  = Parent A  + Parent B
        # child B  = Parent B  + Parent A
        # first assign Parent A fully and leave Parent B's parts blank
        childA = parentA[0:crossPoint] + [None] * (lenChrom - crossPoint)
        childB = [None] * crossPoint + parentA[crossPoint:lenChrom]

        # next we do the  crossover for each gene in the children for the parent B parts
        # since TSP problems cannot have the same gene in chromosome we must fix the remaining parts

        # childA
        # we assign the parts in child A that have no conflict, first we find out what genes
        # in parent B's crossover for child A are not there already in child A ,
        # i.e. those genes that have no conflict
        missingAnotconflict = list(set(parentB[crossPoint:lenChrom]) - set(parentA[0:crossPoint]))
        # then we check if those genes from parent B that have to be crossed over
        # to child A have no conflict,
        for i in range(crossPoint, lenChrom):
            # if they have no conflict they are assigned to child A
            if parentB[i] in missingAnotconflict:
                childA[i] = parentB[i]
        # then we check the remaining genes that due to conflicts
        # are missing from child A compared to parent A
        missingA = list(set(parentA) - set(childA))

        # we check the blank parts of child A and assign them with the missing elements
        for i in range(lenChrom):
            if childA[i] is None:
                # we assign the first part of the missing element and then
                # delete that element so the for loop doesn't have to keep track [8]
                childA[i] = missingA[0]
                del missingA[0]

        # we essentially repeat the same process for child B, except in reverse
        missingBnotconflict = list(set(parentA[0:crossPoint]) - set(parentB[crossPoint:lenChrom]))
        for i in range(0, crossPoint):
            if parentA[i] in missingBnotconflict:
                childB[i] = parentA[i]
        missingB = list(set(parentB) - set(childB))

        for i in range(lenChrom):
            if childB[i] is None:
                childB[i] = missingB[0]
                del missingB[0]

        return childA, childB


    @staticmethod
    def single_swap_mutation(orginChrom):
        # depending on the size of the chromosome, we take 2 random points
        dummyChrom = [i for i in range(len(orginChrom))]
        i, j = random.sample(dummyChrom,2)

        # we swap values of those 2 points
        temp = orginChrom[i]
        orginChrom[i] = orginChrom[j]
        orginChrom[j] = temp
        return orginChrom


    @staticmethod
    def multiple_swap_mutation(originChrom):
        # we do single swap mutation as many times as the mutationTimes
        mutatedChrom = []
        for i in range(self.mutatTime):
            mutatedChrom = self.single_swap_mutation(originChrom)
            originChrom = mutatedChrom
        return mutatedChrom


    @staticmethod
    def inversion_mutation(originChrom):
        # in inversion mutation we slice a strand of the chromosome, invert the order of that slice and
        # place it back into the chromosome
        # depending on the size of the chromosome, we take 2 random points
        dummyChrom = [i for i in range(len(originChrom))]
        i, j = random.sample(dummyChrom,2)

        # we invert the points between i and j, but i must less than j
        if i>j:
            tempIndex = i
            i = j
            j = tempIndex
        mutatedChrom = originChrom[0:i] + originChrom[i:j][::-1] + originChrom[j:len(originChrom)]
        return mutatedChrom


    def evolut_algorithm(self):
        # this is the function for the main evolutionary algorithm
        # timer to measure time take to run one run of the evolutionary algorithm
        start_time = timeit.default_timer()

        # the cost Matrix is set up here
        # self.costMatrix = self.xml_to_matrix()
        self.costMatrix = self.text_to_matrix()
        # to draw the fitness convergence curve, we create a list of the fitness and the fitness evaluation number
        fitness_converg = []

        chromLength = len(self.costMatrix[0])
        # generate population
        PopStart = self.generate_population(chromLength)
        # assess the fitness of the population, creating a list with this format(fitness, population)
        PopFit = []
        for i in range(self.popSize):
            PopFit.append((self.fitness_func(PopStart[i]),PopStart[i]))
        # we sort from ascending, so the fittest first
        PopFit.sort()

        # we run evolution
        for i in range(self.evolutionCycles):
            # print message
            print("Evaluation : " + str(i) + "| " + str(PopFit[0]))
            # we add top fitness and cycle no to the fitness convergence
            fitness_converg.append((PopFit[0][0],i))

            # we pick 2 parents by tournament selection
            parent1 = self.tournament_selection([l for i,l in PopFit],self.tourSize)
            parent2 = self.tournament_selection([l for i,l in PopFit],self.tourSize)
            # we create 2 children by chosen crossover function defined in the method
            if self.crossover_function == 'order':
                child1, child2 = self.single_crossover_ordered(parent1,parent2)
            elif self.crossover_function == 'fix':
                child1, child2 = self.single_crossover_with_fix(parent1, parent2)
            # we allow mutation method to be defined in the function and children are
            # mutated by the chosen function
            if self.mutatMethod == 'S':
                # single swap mutation
                child11 = self.single_swap_mutation(child1)
                child22 = self.single_swap_mutation(child2)
            elif self.mutatMethod == 'M':
                # multi swap mutation
                child11 = self.multiple_swap_mutation(child1)
                child22 = self.multiple_swap_mutation(child2)
            elif self.mutatMethod == 'I':
                child11 = self.inversion_mutation(child1)
                child22 = self.inversion_mutation(child2)

            # evaluate fitness of children
            child11f = self.fitness_func(child11)
            child22f = self.fitness_func(child22)

            # replace the weakest value, ie the last value if the child is better than the weakest
            # since we have sorted the list
            if child11f < PopFit[self.popSize-1][0]:
                PopFit[self.popSize-1] = (child11f,child11)
            PopFit.sort()
            if child22f < PopFit[self.popSize-1][0]:
                PopFit[self.popSize-1] = (child22f,child22)
            PopFit.sort()
        # stop the timer and calculate time by iteration
        end_time = timeit.default_timer()
        time_taken = end_time - start_time

        return time_taken,PopFit[0],fitness_converg

    @staticmethod
    def plot_convergence(data1, titles1, text1, x_pos1, y_pos1,data2,titles2,text2,x_pos2,y_pos2):
        # this function is used to plot the convergence graphs of brazil and burma, if given the dataset
        # convert data in tuple form to list to plot
        y1 = list(zip(*data1))[0]
        x1 = list(zip(*data1))[1]
        y2 = list(zip(*data2))[0]
        x2 = list(zip(*data2))[1]

        # plot 2 subplots, one for data 1 and another for data 2
        fig = plt.figure(figsize=(20,6))
        ax1 = fig.add_subplot(1,2,1)
        ax2 = fig.add_subplot(1,2,2)

        # first subplot customisation, we write time taken as text
        ax1.plot(x1,y1)
        ax1.set_xlabel('Fitness Evaluations')
        ax1.set_ylabel('Fitness')
        ax1.set_title(titles1)
        ax1.text(x_pos1,y_pos1,text1)

        # second subplot customisation
        ax2.plot(x2,y2)
        ax2.set_xlabel('Fitness Evaluations')
        ax2.set_ylabel('Fitness')
        ax2.set_title(titles2)
        ax2.text(x_pos2,y_pos2,text2)

        plt.show()


    def run_experiment(self,finalSize, inialSize, stepSize,expRepeat,csv_filename):
		# OBSOLETE FUNCTION
        # we use this function to run our experiment by varying each factor manually,
        # i.e. the function has to be modified by the user to test what parameter is required
        # it is mainly used to test population size and tournament size, population by tournament ratio
        ans = []
        # we repeat our experiment since our population is random
        for i in range(expRepeat):
            for j in range(inialSize,finalSize,stepSize):
                tim1, best_ans1, convg1 = self.evolut_algorithm()
                ans.append((j,best_ans1[0],tim1))

        ans.sort()

        # since we don't have the computational power to run the entire experiment by scratch
        # we save the results into a chosen .csv file for later retrival [12]

        with open(csv_filename, 'w', newline='') as csv_file:
            csv_writer = csv.writer(csv_file)
            for row in ans:
                csv_writer.writerow(row)
