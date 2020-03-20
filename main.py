def collectForm(form, i):
    endBrac = False
    if form[i] == '(':
        j = i+1
        bracCount = 1
        while (endBrac == False) and j < len(form):
            if form[j] == '(':
                bracCount += 1
            elif form[j] == ')':
                bracCount -= 1
            if bracCount == 0:
                endBrac = True
            else:
                j += 1
        # if brackets were found surrounding a new formula, call parse again
        if endBrac == True:
            return form[i+1:j]
        else:
            return 0
    elif form[i] == ')':
        j = i-1
        bracCount = 1
        while (endBrac == False) and j>=0:
            if form[j] == ')':
                bracCount += 1
            elif form[j] == '(':
                bracCount -= 1
            if bracCount == 0:
                endBrac = True
            else:
                j -=1
        if endBrac == True:
            return form[j+1:i]
        else:
            return 0

def quantEncounter(form, i, startind, globform, flag):
    print('in quantifiers')
    form[i] = 'pq'  # parsed quantifier
    print(form)
    print('in encounterquant, form[i+1]:')
    print(form[i+1])
    if form[i + 1] in variables:
        form[i + 1] = 'pv'  # parsed variable
        print('in variables')
        print(form)
        if form[i + 2] == '(':
            newForm = collectForm(form, i + 2)
            print('newform is ' + str(newForm))
            # if brackets were found surrounding a new formula, call parse again
            if newForm == 0:
                # Invalid brackets. Formula is not properly encompassed.
                print("Given formula is invalid. Error in brackets")
                return 0, globform, flag
            else:
                print('newForm in encounterQuant')
                print(newForm)
                result, globform = parse(newForm, startind + i + 3, globform, flag)
                print('just returned parsing in encounterquant and the result is:')
                print(result)
                print('and globform is: ')
                print(globform)
                if result == 0:
                    print("Given formula is invalid.")
                    return 0, globform, flag
                else:
                    count = i + 3
                    print('form before editing:')
                    print(form)
                    for item in result:
                        form[count] = item
                        count += 1
                    form[i + 1] = 'pv'  # set variable to pv = parsed variable
                    form[i] = 'pq'  # parsed quantifier
                    print('new form after editing')
                    print(form)
                    for j in range(startind + i, startind + i + 2 + len(newForm) + 2):  # +2 so includes brackets
                        globform[j] = flag
                    flag += 1
                    print('form after for loop')
                    print(form)

        elif form[i + 2] == '\\neg':
            form[i + 2] = 'pc'  # parsed connective
            j = 0
            # in case there are more than one neg after another
            while form[j + i + 3] == '\\neg' and (j + i + 3) < len(form) + 1:
                form[j + i + 3] = 'pc'  # parsed connective
                j += 1
            if (j + i + 3) == len(form):
                print("Invalid formula. Error with negs.")
                return 0, globform, flag
            # if there is a bracket after the last neg
            if form[j + i + 3] == '(':
                newForm = collectForm(form, j + i + 3)
                if newForm == 0:
                    print('Given formula is invalid. Error in brackets.')
                    return 0, globform, flag
                else:
                    result, globform = parse(newForm, startind + i + j + 4, globform, flag)
                    if result == 0:
                        print("Formula is invalid")
                        return 0, globform, flag
                    else:
                        count = j + i + 4
                        for item in result:
                            form[count] == item
                            count += 1
                for k in range(startind + i, startind + i + j + 3 + len(newForm) + 2):
                    globform[k] = flag
                flag += 1

            else:
                # the item after the neg should be a formula
                result, globform = parse([form[j + i + 3]], startind + i + j + 3, globform, flag)
                if result == 0:
                    print('Given formula is invalid')
                    return 0, globform, flag
                else:
                    form[j + i + 3] = result[0]
                for k in range(startind + i, startind + i + j + 4):
                    globform[k] = flag
                flag += 1

        else:
            # return next item to check its a formula
            # in next iteration make sure its not a constant or variable
            result, globform = parse([form[i + 2]], startind + i + 2, globform, flag)
            if result == 0:
                print('Invalid formula. Value after quantifier ' + form[i] + ' is not a formula.')
                return 0, globform, flag
            else:
                form[i + 2] = result[0]
            for k in range(startind + i, startind + i + 3):
                globform[k] = flag
            flag += 1

    else:
        # item after a quantifier isn't a variable
        print("Given formula is invalid")
        return 0, globform, flag
    print('form to be returned: ')
    print(form)
    return form, globform, flag




def parse(form, startind, globform, flag):

    for i in range(len(form)):
        print('i is ' + str(i))
        print('form:')
        print(form)
        print('form[i]:')
        print(form[i])

        if form[i] in equality:
            print("Given formula is invalid. Equality found rogue.")
            return 0
        elif form[i] in constants:
            print("Given formula is invalid. Constant found rogue.")
            return 0
        elif form[i] in variables:
            print("Given formula is invalid. Variable found rogue.")
            return 0
        #if a formula of length one is returned, it must be a predicate
        elif len(form) == 1:
            predVal = form[0].replace(',', '')
            if predVal[0] not in predLetters:
                print("Given formula is invalid. Predicate letter not defined")
                return 0
            #Formula of length one is a predicate
            else:
                print('letter is in predletters')
                #Counting number of variable letters in given predicate
                numVar = len(predVal) - 3
                print('numVar ' + str(numVar))
                for item in predicates:
                    #Finding letter in predicates that corresponds to given formula
                    if item[0] == predVal[0]:
                        print('no error')
                        print('num expected '+ str(item[2]))
                        if int(item[2]) != int(numVar):
                            print("Given formula is invalid. Number of variables in predicate is invalid.")
                            return 0
                        else:
                            print("Correct number of variables in predicate")
                            for j in range(2, len(form)):
                                if form[j] != ',':
                                    if form[j] not in variables:
                                        print("Given formula is invalid. Variable in predicate is invalid.")
                                        return 0
                            #Predicate is correct
                            form = ['vf']
                            globform[startind] = flag
                            flag += 1
        elif form[i] == '(':
            if (form[i+1] != 'vf') and (form[i+1] != 'vfe'):
                newForm = collectForm(form, i)
                if newForm == 0:
                    print("Given formula is invalid. Error in brackets.")
                    return 0
                else:
                    result, globform = parse(newForm, startind+i+1, globform, flag)
                    if result == 0:
                        print(','.join(newForm), + ' is an invalid formula.')
                    else:
                        count = i + 1
                        for item in result:
                            form[count] = item
                            count += 1
                        for j in range(startind+i, startind+i+len(newForm)+2 ): #+2 so includes brackets
                            globform[j] = flag
                        flag +=1



        elif form[i] in quantifiers:
            form, globform, flag = quantEncounter(form, i, startind, globform, flag)
            if form == 0:
                return 0

        elif form[i][0] in predLetters:
            result, globform = parse([form[i]], startind+i, globform, flag)
            if result == 0:
                print("Predicate returned as incorrect.")
                return 0
            else:
                print('result')
                print(result)
                form[i] = result[0]
                globform[startind+i] = flag
                flag += 1

        elif len(form[i]) == 2 and form[i][0] == '(':
            if (form[i][1] in constants or form[i][1] in variables) and (form[i+1] in equality) and (form[i+2][0] in variables or form[i+2][0] in constants):
                    form[i] = 'vfe' #valid formula equality
                    form[i+1] = 'vfe'
                    form[i+2] = 'vfe'
                    for k in range(startind+i, startind+i+3):
                        globform[k] = flag
                    flag+=1
            else:
                print('Given formula is invalid. Error in equality.')
                return 0

        elif form[i] in connectives:
            # the item before the connective (already parsed) should be a formula
            # no need to check item before if connective is neg
            if form[i] != "\\neg":
                if form[i - 1] == ')':
                    j = 0
                    while form[i - 1 - j] == ')':
                        j += 1
                    if (form[i - 1 - j] != 'vf') and (form[i - 1 - j] != 'vfe'):
                        print('Given formula is invalid. Item before connective ' + form[i] + ' is not a formula.')
                        return 0
            form[i] = 'pc' #parsed connective
            print('form in connectives section:')
            print(form)
            #if there is a bracket after the connective, it should contain a formula
            if form[i+1] == '(':
                newForm = collectForm(form, i+1)
                if newForm == 0:
                    print('Given formula is invalid. Error in brackets.')
                    return 0
                else:
                    result, globform = parse(newForm, startind+i+2, globform, flag)
                    if result == 0:
                        print("Formula is invalid")
                        return 0
                    else:
                        count = i + 2
                        for item in result:
                            form[count] == item
                            count += 1
                        for j in range(startind+i+1, startind+i+1+len(newForm)+2):
                            globform[k] = flag
                        flag +=1

            #if there is a neg after the connective

            elif form[i+1] == '\\neg':
                form[i+1] = 'pc'
                print('form in connectives part neg')
                print(form)
                j= 0
                #in case there are more than one neg after another
                while form[j+i+2] == '\\neg' and (j +i+2) < len(form) + 1:
                    form[j+i+2] = 'pc'
                    j += 1
                if (j+i+2) == len(form):
                    print("Invalid formula. Error with negs.")
                    return 0
                #if there is a bracket after the last neg
                if form[j+i+2] == '(':
                    newForm = collectForm(form, j+i+2)
                    if newForm == 0:
                        print('Given formula is invalid. Error in brackets.')
                        return 0
                    else:
                        result, globform = parse(newForm, startind+j+i+3, globform, flag)
                        if result == 0:
                            print("Formula is invalid")
                            return 0
                        else:
                            count = j + i + 3
                            for item in result:
                                form[count] == item
                                count += 1
                            for k in range(startind+i+1, startind+i+j+2+len(newForm)+2): # i+j+2 = (
                                globform[k] = flag
                            flag +=1

                else:
                    #the item after the neg should be a formula
                    result, globform = parse([form[j + i + 2]], startind+i+j+2, globform, flag)
                    if result == 0:
                        print('Given formula is invalid')
                        return 0
                    else:
                        form[j + i + 2] = result[0]
                        for k in range(startind+i+1, startind+j+i+2):
                            globform[k] = flag
                        flag+=1
            elif form[i+1] in quantifiers:
                form, globform, flag = quantEncounter(form, i+1, startind, globform, flag)
                if form == 0:
                    return 0


            #the single item after the connective should be a formula
            else:
                result, globform = parse([form[i+1]], startind+i+1, globform, flag)
                if result == 0:
                    print('Given formula is invalid')
                    return 0
                else:
                    form[i+1] = result[0]
                    globform[startind+i+1] = flag
                    flag +=1

    print('Parsed form:')
    print(form)
    return form, globform

with open('example.txt') as inpFile:
    inpArray = inpFile.readlines()
print(inpArray)

#Separate different parts of language definition

variables = inpArray[0]
variables = variables.replace("\n", "")
variables = variables.split(' ')
variables.pop(0)
print(variables)

constants = inpArray[1]
constants = constants.replace("\n", "")
constants = constants.split(' ')
constants.pop(0)
print(constants)

predicates = inpArray[2]
predicates = predicates.replace("\n", "")
predicates = predicates.split(' ')
predicates.pop(0)
print(predicates)

equality = inpArray[3]
equality = equality.replace("\n", "")
equality = equality.split(' ')
equality.pop(0)
print(equality)

connectives = inpArray[4]
connectives = connectives.replace("\n", "")
connectives = connectives.split(' ')
connectives.pop(0)
print(connectives)

quantifiers = inpArray[5]
quantifiers = quantifiers.replace("\n", "")
quantifiers = quantifiers.split(' ')
quantifiers.pop(0)
print(quantifiers)

#Printing out grammar of language defined

terminal = variables + constants + predicates
nonterminal = ['S', 'D', 'V', 'A', 'E', 'F', 'G']
print('S -> (S) | SDS | NS | A | E | \epsilon')
varPrint = ' | '.join(variables)
print('V -> ' + varPrint)
connPrint = ' | '.join(connectives)
print('D -> ' + connPrint)
quantifiersProd = []
for i in range(0, len(quantifiers)):
    quantifiersProd.append(quantifiers[i] + ' VS')
quantPrint = ' | '.join(quantifiersProd)
print('N -> ' + quantPrint)
predProd = []
predLetters = []
for i in range(len(predicates)):
    predProd.append(predicates[i][0] + '(')
    predLetters.append(predicates[i][0])
    for j in range(int(predicates[i][2])):
        predProd[i] = predProd[i] + 'V'
    predProd[i] = predProd[i] + ')'
predProdPrint = ' | '.join(predProd)
print('A -> ' + predProdPrint)
if equality != []:
    print('E -> F' + equality[0] + 'F')
constPrint = ' | '.join(constants)
if (constants != []) and (variables != []):
    print('F -> V | C')

#Breaking up formula into list

formula = inpArray[6]
formula = formula.split()
formula.pop(0)
print(formula)


finalform = formula
flag = 0

result, finalform = parse(formula, 0, finalform, flag)
if result == 0:
    print('result = 0. invalid formula')
else:
    print('Result:')
    print(result)
    print('finalform/globform:')
    print(finalform)







