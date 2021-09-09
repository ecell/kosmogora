from cobra import Model, Reaction, Metabolite
import cobra.io

model = Model('example_model')

A = Metabolite('A', compartment='c')
B = Metabolite('B', compartment='c')
C = Metabolite('C', compartment='c')

Atrans = Reaction('Atrans')
Atrans.add_metabolites({A: +1})

Btrans = Reaction('Btrans')
Btrans.add_metabolites({B: -1})

Ctrans = Reaction('Ctrans')
Ctrans.add_metabolites({C: -1})

AtoB = Reaction('AtoB')
AtoB.add_metabolites({A: -1, B: +1})

AtoC = Reaction('AtoC')
AtoC.add_metabolites({A: -1, C: +1})

BtoC = Reaction('CtoB')
BtoC.add_metabolites({C: -1, B: +1})

model.add_reactions([Atrans, Btrans, Ctrans, AtoB, AtoC, BtoC])
model.objective = Btrans

# solution = model.optimize()

cobra.io.write_sbml_model(model, "sample1.xml")
