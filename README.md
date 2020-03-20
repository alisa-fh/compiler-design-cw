# First Order Formulae Parser
I have developed a parser which takes in inputs, defining a language. This can include
its variables, connectives, predicates of various aritys and more. A formula is also read in
from the same input file and parsed, to see if it correctly conforms to the language. If so, a 
tree is built representing the formula.



## Installing packages

Install graphviz to be used on Python 3.7.4:

```
pip install graphviz
```
Ensure the following is added to the end of your User Variables PATH:


```
;C:\Program Files(x86)\Graphviz2.38\bin
```

Next answer Prompts to user input that client.py was run in to make your order!

## How to run

In the terminal type the following command, where [filename] is the name of your
input file. The input file must be in the same directory as the main program, main.py

```
python main.py [filename]
```
The grammar will now be outputted, through the terminal, in a format similar to the following:

```
S -> (S) | SDS | NS | A | E | \neg S | \epsilon
V -> w | x | y | z
D -> \land | \lor | \implies | \iff | \neg
N -> \exists VS | \forall VS
A -> P(VV) | Q(V)
E -> F=F
C -> constC | constD
F -> V | C
```

The given formula will automatically be parsed.  
If the formula is determined to be invalid, this will be communicated via the
terminal, through brief error messages. More extensive error messages can be found in the log.txt file
in the same directory.  
  
If a formula is determined to be valid, this will also be communicated via the terminal. In addition, this will
be documented in the log.txt. A parse tree will be generated and outputted automatically. This can be found in the 
directory of the program under the name 'fograph.pdf'.  
In the event of a success, a tokenised formula will also be outputted for your interest.
The key to this is shown below:
```
pq - parsed quantifier
pv - parsed variable
pc - parsed constant
vf - valid formula
vfe - valid formula equality (makes up part of an equality atom)
```