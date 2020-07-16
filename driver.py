import re, json, sys
from statements import RelationshipStatement, DelegationStatement, Policy, Delegation
from graph import Node, Edge, Graph

def main():
    try:
        policyFile = open("temp.json", "r")
        fileDict = json.load(policyFile)

    except ValueError as e:
        print("Error decoding policy file: ")
        print(e)
        sys.exit(0)

    #grab the dict that maps characters to the permission they represent
    permissions = fileDict["permission types"]

    #process relationships
    socialNetwork, nodes = buildSocialNetwork(fileDict["relationships"])

    #process policies, replace with policy objects
    resources = fileDict["resources"]
    for key in resources:
        resource = resources[key]
        policy = resource["policy"]
        resource["policy"] = processPolicy(policy)

    #process delegations. valid delegations turned into Delegation objects and
    #appended to the policy object for the given resource
    processDelegations(resources, socialNetwork, nodes, permissions)

    while(True):
        print("Resource: ", end = "")
        obj = input().strip()
        print("Accessor: ", end = "")
        accessor = input().strip()
        print("Permission: ", end = "")
        perm = input().strip()
        print(hasAccess(obj, accessor, perm, socialNetwork, resources, nodes))

# Processes the delegations for each resource. If a delegation is valid, it is turned into
# a Delegation object and appended to the policy object of the resource in question
# A delegation is valid iff
#   -there there is a delegation statement in the policy that allows a delegator to delegate
#   -the delegator is delegating permissions that they actually have
def processDelegations(resources, socialNetwork, nodes, permissions):
    for resource in resources:
        #if delegations exist for this resource, process them. otherwise skip this resource
        if "delegations" not in resources[resource]:
            continue

        delegations = resources[resource]["delegations"]
        owner = resources[resource]["owner"]
        policy = resources[resource]["policy"]

        for delegator in delegations:
            #check all delegation statements in this policy, see if any connect owner to delegator,
            #allowing delegator to delegate
            for statement in policy.statements:
                if type(statement) is DelegationStatement:
                    relationshipStatement = statement.relationship
                    ret = relatedVia(relationshipStatement, owner, delegator, socialNetwork, nodes)

                    #if accessor isnt related to owner via this relationship statement, move on to
                    #next delegation statement in resource's policy
                    if not ret:
                        continue

                    #make sure delegator actually has the permissions they are trying to delegate
                    perms = re.findall("\(\w+\)", delegations[delegator]["delegates"])[0]
                    perms = perms[1:len(perms)-1]
                    for c in perms:
                        print("checking {} perm {}".format(delegator, c))
                        #make sure permission exists in permission dict
                        if c not in permissions:
                            errorString = "Nonexistent permission used in delegation statement: " + c
                            raise SyntaxError(errorString)

                        #make sure delegator has this permission
                        if not hasAccess(resource, delegator, c, socialNetwork, resources, nodes):
                            errorString = "Permissions cannot be delegated by individuals without permissions in question\n"
                            errorString = errorString + "{} attempted to delegate {} permission for resource {}".format(delegator, c, resource)
                            raise SyntaxError(errorString)

                    #ok to delegate, create new relationship statement and append to policy
                    #add permissions as part of relationship string. dumb fix
                    delegates = delegations[delegator]["delegates"]
                    delegation = Delegation(parseRelationshipStatement(delegates, False), delegator)
                    policy.statements.append(delegation)
                    break

            #if no Delegation statements allow delegator to delegate raise Error
            else:
                raise SyntaxError("Invalid attempt to delegate: {} attempted to delegate for resource {}".format(delegator, resource))


# Answers the question "does accessor have access to resource with permission"
# ex. hasAccess("file.txt", "Alice", "r", ....) answers whether Alice has read permission for file.txt
# social network is a graph representing the social network
# resources is the dict of resources after replacing policy strings with policy objects during preprocessing
# nodes is a the dict mapping string representations of individuals to corresponding Node objects
# permission must be given as a character
def hasAccess(resource, accessor, permission, socialNetwork, resources, nodes):
    owner = resources[resource]["owner"]
    policy = resources[resource]["policy"]

    for statement in policy.statements:
        #actual delegation statements not used to determine access
        #delegations themselves cross referenced with Delegation Statements and
        #turned into Delegation objects during preprocessing (processDelegations method)
        if(type(statement) is DelegationStatement):
            continue

        if type(statement) is RelationshipStatement:
            #check whether this statement can even grant the wanted permission
            if statement.permissions.find(permission) == -1:
                continue

            #check whether this relationship connects owner to accessor
            related = relatedVia(statement, owner, accessor, socialNetwork, nodes)

        if type(statement) is Delegation:
            #check whether this statement can even grant the wanted permission
            if statement.relationship.permissions.find(permission) == -1:
                continue

            #check whether this relationship connects delegator to accessor
            delegator = statement.delegator
            related = relatedVia(statement.relationship, delegator, accessor, socialNetwork, nodes)

        if related:
             return True
    return False

# Determines whether owner is related to accessor via relationshipStatement
def relatedVia(statement, owner, accessor, socialNetwork, nodes):
    #check special cases for relationship statement
    if statement.everyone:
        return True #T
    elif statement.owner and not statement.negation:
        if owner == accessor :
            return True #a
        else:
            return False
    elif statement.owner and statement.negation:
        if owner != accessor:
            return True# !a
        else:
            return False

    #evaluate relationship of owner and accessor
    if owner not in nodes or accessor not in nodes:
        return False
    ownerNode = nodes[owner]
    accessorNode = nodes[accessor]
    ret = socialNetwork.hasRelationship(statement.labels, ownerNode, accessorNode)

    if statement.negation:
        ret = not ret

    return ret

# Turns the relationship dictionary from the policy file into a social network graph
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

# Takes a string representation of a policy and returns a policy object to represent it
# Checks syntax along the way, raises errors if improper syntax
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


# Takes an individual relationship statement, parses it,
# and returns a corresponding relationshipStatement object
def parseRelationshipStatement(statement, isPartOfDelegationStatement, delegator = None):
    syntaxErrorString = "Error in policy syntax. Relationship statement written incorrectly: " + statement

    #verify that statement takes the proper form
    if isPartOfDelegationStatement and re.search("^(!?(<-?\w+>)*a|T)$", statement) is None:
        raise SyntaxError(syntaxErrorString)
    if (not isPartOfDelegationStatement) and re.search("^(!?(<-?\w+>)*(a|d)|T)(\(\w+\))$", statement) is None:
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
    if statement[length -1] != "a" and statement[length-1] !="d" :
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

# Takes a string representation of a delegation statement, parses it,
# returns a corresponding DelegationStatement object
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
