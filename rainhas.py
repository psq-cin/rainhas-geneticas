#!/usr/bin/python3

'''
Solution for the eight queens puzzle, searching the solution space
with a genetic algorithm.
Pedro Queiroga, 2019.
Tópicos Avançados em Inteligência Artificial com Paulo Salgado,
Computação Bioinspirada.
'''

import random

class RainhasGeneticas:
    """A class that represents a set of tunable parameters"""

    def __init__(self, pop_init_size=10, mutation_chance=0.3, recombination_chance=0.9, grow_population=False, population_limit=0, die_by_age=False, converge_all=False, simple_recombination=False, simple_mutation=False, roulette=False, verbose=True):
        self.pop_init_size = pop_init_size
        self.mutation_chance = mutation_chance
        self.recombination_chance = recombination_chance
        self.grow_population = grow_population
        self.population_limit = population_limit
        self.die_by_age = die_by_age
        self.converge_all = converge_all
        self.simple_recombination = simple_recombination
        self.simple_mutation = simple_mutation
        self.roulette = roulette
        self.verbose = verbose
        self.population = []
        self.current_generation = 0
        self.__initial_gene=[0,1,2,3,4,5,6,7]

    def initialise(self):
        # population is represented as an array where each 
        # each index is the column, and the elements are the lines.
        # ex: [0,1,2,3,4,5,6,7] is a diagonal of queens.

        self.population = [ random.sample(self.__initial_gene, len(self.__initial_gene)) for i in range(self.pop_init_size) ]
        self.current_generation = 0

    # used for bitstring representation
    def __bs_fisher_yates(self, s, element_len=3):
        """bs stands for bit string!"""
        i = int(len(s)/element_len) - 1
        while i > 0:
            j = random.randint(0,i)

            trans_i=i*element_len
            trans_j=j*element_len

            for k in range(element_len):
                s[trans_j+k],s[trans_i+k]=s[trans_i+k],s[trans_j+k]

            i -= 1
        return s

    def evaluate(self, population):
        evaluation = [ self.eval_indie(i) for i in population ]
        return evaluation

    def eval_indie(self, indie):
        penalty = 0
        seen = []
        for (idx, val) in enumerate(indie):
            for s in seen:
                if val == s[1]:
                    penalty += 1
            seen.append((idx, val))
            if not set(seen).isdisjoint(self.diagonal_hits((idx, val))):
                penalty += 1
        return penalty

    def diagonal_hits(self, line_column):
        line,column = line_column
        positions_hit = []
        for i in range(1,8):
            if line+i < 8:
                if column+i < 8:
                    positions_hit.append((line+i, column+i))
                if column-i >= 0:
                    positions_hit.append((line+i, column-i))
            if line-i >= 0:
                if column-i >= 0:
                    positions_hit.append((line-i, column-i))
                if column+i < 8:
                    positions_hit.append((line-i, column+i))
        return positions_hit

    def select_parents_tournament(self):
        # choose 5 random individuals, and then get the best 2 of those.
        # pick_n = int(0.5*len(self.population))
        random_five_parents = random.choices(self.population, k=5)
        parents_evaluation = self.evaluate(random_five_parents)
        best_two_parents,_ = zip(*sorted(zip(random_five_parents, parents_evaluation), key=lambda x: x[1]))
        return list(best_two_parents[:2])

    def select_parents_roulette(self, evaluation):
        w = [ 1/(1+i) for i in evaluation ]
        random_parents = random.choices(self.population, weights=w, k=2)
        return random_parents

    def recombine(self, parents):
        # my recombine function will choose a random number to cut,
        # and then find where they appear on each other's genes,
        # so i'll keep it always a permutation.
        p1,p2 = parents[0].copy(),parents[1].copy()
        if random.random() < self.recombination_chance:
            max_cuttings = int(len(p1) / 4) # p1 and p2 are the same length
            to_cut = random.choices(range(len(p1)),k=max_cuttings)
            for v in to_cut:
                for (idx,j) in enumerate(p2):
                    if p1[v] == j:
                        # i'll exchange the indexes
                        p1[v],p1[idx]=p1[idx],p1[v]
                        p2[v],p2[idx]=p2[idx],p2[v]
                    else:
                        continue
        return [p1,p2]

    def old_recombine(self, parents):
        """recombination as before full permutation manipulation"""
        p1,p2 = parents[0].copy(), parents[1].copy()
        if random.random() < self.recombination_chance:
            # i'll cut a section that will be correspond to half of the gene
            # or lower. least being a fourth of the genetic information...
            to_cut = random.choice(range(int(len(p1)/4), int(len(p1)/2)+1))
            # insert recombination chance here, 90% as seen in class.
            p1[:to_cut],p2[:to_cut] = p2[:to_cut],p1[:to_cut]

        return [p1,p2]

    def old_mutate(self, offspring):
        """mutation as before full permutation manipulation"""
        # this mutation function will use gray code
        for o in offspring:
            for (idx,_) in enumerate(o):
                before_mutation = o[idx]
                gray = self.binary_to_gray(before_mutation)
                if random.random() < self.mutation_chance:
                    gray = gray ^ 1
                if random.random() < self.mutation_chance:
                    gray = gray ^ 2
                if random.random() < self.mutation_chance:
                    gray = gray ^ 4
                    
                o[idx] = self.gray_to_binary(gray)
                
        return offspring

    def binary_to_gray(self, num):
        """
         This function converts an unsigned binary
         number to reflected binary Gray code.
         The operator >> is shift right. The operator ^ is exclusive or.
        taken from wikipedia https://en.wikipedia.org/wiki/Gray_code
        """
        return num ^ (num >> 1)
    
    def gray_to_binary(self, num):
        """
         This function converts a reflected binary
         Gray code number to a binary number.
         Each Gray code bit is exclusive-ored with all
         more significant bits.
        taken from wikipedia https://en.wikipedia.org/wiki/Gray_code
        """
        mask = num >> 1

        while (mask != 0):
            num = num ^ mask
            mask = mask >> 1

        return num
    
    def mutate(self, offspring):
        # i'll mutate an individual by permutating random indexes.
        for o in offspring:
            for (idx,_) in enumerate(o):
                if random.random() < self.mutation_chance:
                    other_idx=random.randrange(8)
                    o[idx],o[other_idx]=o[other_idx],o[idx]

        return offspring

    def select_survivors(self):
        # two worst individuals won't be considered for the next generation.
        evaluation = self.evaluate(self.population)
        minney = evaluation.index(max(evaluation))
        del self.population[minney]
        del evaluation[minney]
        minney = evaluation.index(max(evaluation))
        del self.population[minney]

    def visualize_gene(self, g):
        for i in g:
            for j in range(8):
                if j==i:
                    print('q',end='')
                else:
                    print('.',end='')
                if j < 7:
                    print(' ', end='')
            print()

    def solve_it(self):
        self.initialise()
        evaluation = self.evaluate(self.population)
        func = min
        occ=0
        if self.converge_all:
            func = max
        while func(evaluation) != 0 and self.current_generation < 20000:
            parents = []
            if self.roulette:
                parents = self.select_parents_roulette(evaluation)
            else:
                parents = self.select_parents_tournament()
            offspring = []
            if self.simple_recombination:
                offspring = self.old_recombine(parents)
            else:
                offspring = self.recombine(parents)
            if self.simple_mutation:
                offspring = self.old_mutate(offspring)
            else:
                offspring = self.mutate(offspring)
            if self.grow_population:
                if len(self.population) < self.population_limit: # controle populacional
                    self.population = self.population + offspring
            if self.die_by_age:
                if self.current_generation % 10 == 0: # morte por idade
                    self.population = self.population[2:]
            self.select_survivors()
            self.population = self.population + offspring
            evaluation = self.evaluate(self.population)
            if self.verbose and self.current_generation % 500 == 0:
                print('current generation:',self.current_generation)
                print(evaluation)
                print(self.population)
            self.current_generation += 1
        if self.verbose:
            print('size of population =', len(self.population))
            print('min(evaluation) =', min(evaluation))
            print('current generation =', self.current_generation)
            solution = self.population[evaluation.index(min(evaluation))]
            print('eval_indie(solution) =', self.eval_indie(solution))
            print(solution)
            self.visualize_gene(solution)
        
        end_result = {
            "success": min(evaluation)==0,
            "populationEndSize": len(self.population),
            "populationInitSize": self.pop_init_size,
            "evaluation": evaluation,
            "population": self.population,
            "numberOfGenerations": self.current_generation,
            "worstIndividual": max(evaluation),
            "averageIndividual": sum(evaluation)/len(evaluation)
        }
        return end_result


    def evaluate_test(self, a):
        print(self.evaluate([a]))

    def diagonal_hits_test(self):
        print('diagonal_hits_tests...')
        assert self.diagonal_hits((0,0)) == [(1,1), (2,2), (3,3), (4,4), (5,5), (6,6), (7,7)], ('erro: ', self.diagonal_hits((1,1)))
        print('OK')

    def eval_indie_test(self):
        chosen = [2, 7, 0, 6, 1, 3, 4, 5]
        print(chosen)
        print('-> %d' % (self.eval_indie(chosen)))

    def select_parents_test(self):
        self.pop_init_size=10
        self.initialise()
        for i in self.select_parents():
            print(i)

    def recombine_test(self):
        for _ in range(1):
            self.pop_init_size=10
            p = self.initialise()[:2]
            print(p[0])
            print(p[1])
            p = self.recombine(p)
            print(p[0])
            print(p[1])

    def mutate_test(self):
        self.pop_init_size=10
        indie = [self.initialise()[1]]
        for i in indie:
            print(i)
        mutated = self.mutate(indie)
        for i in mutated:
            print(i)
