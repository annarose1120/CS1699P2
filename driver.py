import re, json, sys
from statements import RelationshipStatement, DelegationStatement, Policy
from graph import Node, Edge, Graph


def main():
    #preprocess the policy file
    #COMMAND LINE ARG =>policy file
    #read in policy file, turn into a dict
    try:
        policyFile = open("temp.json", "r")
        fileDict = json.load(policyFile)

    except ValueError as e:
        print("Error decoding policy file: ")
        print(e)
        sys.exit(0)

    #process relationships
    socialNetwork, nodes = buildSocialNetwork(fileDict["relationships"])

    #process policies, replace with policy objects
    resources = fileDict["resources"]
    for key in resources:
        resource = resources[key]
        policy = resource["policy"]
        resource["policy"] = processPolicy(policy)

    #grab the dict that maps characters to the permission they represent
    permissions = fileDict["permission types"]

    while(True):
        print("Resource: ", end = "")
        obj = input().strip()
        print("Accessor: ", end = "")
        accessor = input().strip()
        print("Permission: ", end = "")
        perm = input().strip()
        print(hasAccess(obj, accessor, perm, socialNetwork, resources, nodes))

#answers the question "does accessor have access to resource with permission"
#ex. hasAccess("file.txt", "Alice", "r") answers whether Alice has read permission for file.txt
#permission must be given as a character
def hasAccess(resource, accessor, permission, socialNetwork, resources, nodes):
    owner = resources[resource]["owner"]
    policy = resources[resource]["policy"]
    for statement in policy.statements:
        #actual delegation statements not used. turned into relationship statements during preprocessing
        if(type(statement) is DelegationStatement):
            continue
        #check whether this statement can even grant the wanted permission
        if statement.permissions.find(permission) == -1:
            continue
        #check special cases for relationship statement
        if statement.everyone:
            return True #T()
        elif statement.owner and not statement.negation:
            if owner == accessor :
                return True #a()
            else:
                continue
        elif statement.owner and statement.negation:
            if owner != accessor:
                return True# !a
            else:
                continue

        #evaluate relationship of owner and accessor
        ownerNode = nodes[owner]
        accessorNode = nodes[accessor]
        ret = socialNetwork.hasRelationship(statement.labels, ownerNode, accessorNode)

        if statement.negation:
            ret = not ret
        if ret:
            return True
    return False



#turns the relationship dictionary from the policy file into a social network graph
def buildSocialNetwork(relationships):
    if type(relationships) is not dict:
        raise TypeError("Relationships in policy file must take the form of a dictionary")
    socialNetwork = Graph()
    nodes = {}                  #all people seen so far, maps string name to their node
                                #to avoid duplicate Nodes

    #turn each relationship into an edge in the social network graph
    for key in relationships:
        relationshipArr = relationships[key]
        if type(relationshipArr) is not list:
            raise SyntaxError("Relationships in policy file improperly formatted")

        for relationship in relationshipArr:
            if type(relationship) is not str:
                raise SyntaxError("Relationships in policy file improperly formatted")

            individuals = relationship.split(",")
            if len(individuals) != 2:
                raise(SyntaxError("Relationships in policy file improperly formatted"))
            #remove leading and trailing whitespace around names
            individuals[0] = individuals[0].strip()
            individuals[1] = individuals[1].strip()

            #check if a node has been made for each person in this relationship
            #if not, make a new one
            if individuals[0] in nodes:
                left = nodes[individuals[0]]
            else:
                left = Node(individuals[0])
                nodes[individuals[0]] = left

            if individuals[1] in nodes:
                right = nodes[individuals[1]]
            else:
                right = Node(individuals[1])
                nodes[individuals[1]] = right

            socialNetwork.addEdge(key, left, right)

    return socialNetwork, nodes

#takes a string representation of a policy and returns a policy object to represent it
#checks syntax along the way, raises errors if improper syntax
def processPolicy(policy):
    #to hold to array of statement objects
    resultArray = []

    #divide policy into statements
    statements = policy.split("|")
    numOr = policy.count("|")
    if len(statements) != numOr + 1:
        raise SyntaxError("Error in policy syntax. Disjunction \"|\" must appear between 2 statements")

    for statement in statements:
        statement = statement.strip()
        if statement[0] == "$":
            resultArray.append(parseDelegationStatement(statement))
        else:
            resultArray.append(parseRelationshipStatement(statement, False))
    newPolicy = Policy(resultArray)
    return newPolicy


#takes an individual relationship statement, parses it,
#and returns a corresponding relationshipStatement object
def parseRelationshipStatement(statement, isPartOfDelegationStatement):
    syntaxErrorString = "Error in policy syntax. Relationship statement written incorrectly: " + statement

    #verify that statement takes the proper form
    if isPartOfDelegationStatement and re.search("^(!?(<-?\w+>)*a|T)$", statement) is None:
        raise SyntaxError(syntaxErrorString)
    if (not isPartOfDelegationStatement) and re.search("^(!?(<-?\w+>)*a|T)(\(\w+\))$", statement) is None:
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
        return RelationshipStatement(owner = True, everyone = False, negation = False, permissions = permissions)

    elif statement == "!a":
        return RelationshipStatement(owner = True, everyone = False, negation = True, permissions = permissions)

    elif statement == "T":
        return RelationshipStatement(owner = False, everyone = True, negation = False, permissions = permissions)

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
    return RelationshipStatement(owner = False, everyone = False, negation = negation, labels = matches, permissions = permissions)

#takes a string representation of a delegation statement, parses it,
#returns a corresponding DelegationStatement object
def parseDelegationStatement(statement):

    syntaxErrorString = "Error in policy syntax. Delegation statement written incorrectly: " + statement
    #make sure delegation statement starts with $( and ends with )
    #remove these characters so we end up with a RelationshipStatement object
    if statement[0] != "$":
        raise SyntaxError(syntaxErrorString)
    else:
        statement = statement[1:]
    if statement[0] != "(":
        raise SyntaxError(syntaxErrorString)
    else:
        statement = statement[1:]
    if statement[len(statement) - 1] != ")":
        raise SyntaxError(syntaxErrorString)
    else:
        statement = statement[:len(statement) - 1]

    #TODO: make sure there is no permissions argument!!
    if re.search("^(!?(<-?\w+>)*a|T)$", statement) is None:
        raise SyntaxError(syntaxErrorString)

    #what is left should be a relationship statement
    relationshipStatement = parseRelationshipStatement(statement, True)
    return DelegationStatement(relationshipStatement)





if __name__ == "__main__":
    main()
