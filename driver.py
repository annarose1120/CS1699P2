import re
from statements import relationshipStatement
syntaxErrorString = "Syntax error in policy file"

def main():
    #preprocess the policy file
    #READ IN JSON TO DICT
    ret = parseRelationshipStatement("!<friend><-parent><-parent>a(r)")
    ret.printStatement()

#takes a string representation of a policy and returns an array of statement objects
#that represent that policy
#checks syntax along the way, raises errors if improper syntax
def processPolicy(policy):
    #to hold to array of statement objects
    resultArray = []

    #divide policy into statements
    statements = policy.split("|")
    numOr = policy.count("|")
    if len(statements) != numOr + 1:
        raise SyntaxError(syntaxErrorString)

#takes an individual relationship statement, parses it,
#and returns a corresponding relationshipStatement object
def parseRelationshipStatement(statement):
    #verify that statement takes the proper form
    #option 1:
    #may begin with !, may have one or more relationship identifiers enclosed in < >
    #must have a to represent the owner, may be followed by permissions enclosed in ( )
    #option 2:
    #T, may be followed by permissions enclosed in ( )

    if re.search("^(!?(<-?\w+>)*a|T)(\(\w+\))?$", statement) is None:
        raise SyntaxError(syntaxErrorString)

    #separate out permissions if applicable
    firstParen = statement.find("(")
    secondParen = statement.find(")")
    if(firstParen != -1):
        permissions = statement[firstParen + 1: secondParen]
        statement = statement[:firstParen]
    else:
        permissions = None

    #special cases
    if statement == "a":
        return relationshipStatement(owner = True, everyone = False, negation = False, permissions = permissions)

    elif statement == "!a":
        return relationshipStatement(owner = True, everyone = False, negation = True, permissions = permissions)

    elif statement == "T":
        return relationshipStatement(owner = False, everyone = True, negation = False, permissions = permissions)

    #for longer statements
    #process and remove ! at beginning, if applicable
    if statement[0] == "!":
        negation = True
        statement = statement[1:]
    else:
        negation = False

    #check that statement terminates with a, remove it
    length = len(statement)
    if statement[length -1] != "a":
        raise SyntaxError(syntaxErrorString)
    else:
        statement = statement [: length - 1]

    #verify that remaining strings take the form <relationship><relationship>....
    if re.search("^(<-?\w+>)+$", statement) is None:
        raise SyntaxError(syntaxErrorString)

    #turn the remaining statement into a list of relationship identifiers
    #ex. <friend><parent><sibling> => ["friend", "parent", "sibling"]
    matches = re.findall("<-?\w+>", statement)
    matches = [match[1:len(match) - 1] for match in matches]
    return relationshipStatement(owner = False, everyone = False, negation = negation, labels = matches, permissions = permissions)







if __name__ == "__main__":
    main()
