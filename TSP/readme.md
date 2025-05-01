Traveling Salesman Problem
--------------------------------
The Traveling Salesman Problem is where a Salesman has to travel to all given cities and this section explores algorithms that selects the solution that takes the least distance.
------------------------------------



  The class works using the following steps:
  1. Convert the datafiles to a cost matrix that contains the distance of all possible cities combinations.
  2. Generate a population of possible paths modeled as genetic chromosomes and calculate their distances.
  3. Using tournament selection, select a bunch of chromosomes (possibles paths), per two chromosomes do a crossover
     forming two children and then mutate the children.
  4. Reintroduce all the children to the intial population if they are better than the initial population.
  5. Repeat this evolution cycle for as many times as required.
