from GeneticAlgorithm import *
import os

# the data files are in the dataset directory, use the code to get the dataset file irrelevant of personal directories
data1_path = os.path.abspath(os.path.join(os.path.dirname(__file__),'..','datasets','a280-n279.txt'))
data2_path = os.path.abspath(os.path.join(os.path.dirname(__file__),'..','datasets','a280-n1395.txt'))


# simply input the following parameters: the file path,  population size, iterations required,tournament size;
# the mutation parameter, 'S' for single swap mutation, 'M' for multiple mutations, 'I' for inversion mutation
# if 'M' is chosen, choose the number of multiple mutations, if 'M' is not chosen this variable is not considered
# lastly choose the crossover operator, 'order' for ordered crossover or 'fix' for crossover with fix

Data1 = GeneticAlgorithm(data1_path,2000,5000,180,'S','order')
tim1, best_ans1,convg1 = Data1.evolut_algorithm()


Data2 = GeneticAlgorithm(data2_path,2000,5000,180,'I','order')
tim2, best_ans2,convg2 = Data2.evolut_algorithm()


# this section prints the optimal answer, its fitness and the executed time
# print('The optimal answer is: ',best_ans1[1])
# print('Its fitness is: ',best_ans1[0])
# print(f'It took {tim1} seconds to execute')

# this section is used to plot the convergence curves and compare other datasets,
text1 = 'Time taken: ' + str(round(tim1,2)) + 's'
text2 = 'Time taken: ' + str(round(tim2,2)) + 's'
Data1.plot_convergence(convg1,'Data 1 Convergence Curve',text1,7000,3800,
                 convg2,'Data 2 Convergence Curve',text2,7000,90000)
