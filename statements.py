#The classes DelegationStatement, RelationshipStatement, Delegation,
#and Policy are used to represent the policy associated with a resource.
#In the policy file, the policy of an object is represented as a string,
#a disjunction of delegation statements and relationship statements.
#During preprocessing, these statements are turned into DelegationStatement objects
#and Relationship Statement objects, respectively.
#This list of statements are used to define a Policy object, which is then associated with the resource.
#Then, the actul delegations are cross-referenced with DelegationStatements in the policy
#object and turned into Delegation objects if they are determined to be valid.
#These Delegation objects are then appended to the list of objects in the policy object.
#When actually deciding access, only the RelationshipStatement and Delegation objects
#are consulted. After processDelegations, the Delegation objects in the policy are ignored.


#to represent the processed form of a relationship statement from the policy file
#Ex. processed form of <friend><parent>a(rwx)
class RelationshipStatement:
    #owner =boolean, whether or not relationship is either "a" or "!a"
    #everyone = boolean, whether or not relationship is "T"
    #negation = boolean, whether or not relationship begins with !
    #labels = String [], list of relationship identifiers
    #permissions = string, which permissions are granted to people with this relationship
    def __init__(self, owner, everyone, negation, labels = None , permissions = None):

        self.owner = owner
        self.everyone = everyone
        self.negation = negation
        self.labels = labels
        self.permissions = permissions

    def printStatement(self):
        print("Owner: {}".format(self.owner))
        print("Everyone: {}".format(self.everyone))
        print("Negation: {}".format(self.negation))
        print("Labels: ", end = "")
        if(self.labels != None):
            for label in self.labels:
                print("{}, ".format(label), end = "")
        print()
        if(self.permissions != None):
            print("Permissions: {}".format(self.permissions))

#to represent to processed form of a delegation statement
#to represent processed form of $(<parent>a)
class DelegationStatement:
    def __init__(self, relationship):
        if not isinstance(relationship, RelationshipStatement):
            raise TypeError("Delegation class constructor must be given a RelationshipStatement")
        self.relationship = relationship

    def printStatement(self):
        self.relationship.printStatement()

#to represent the processed form of a delegation from the delegations in the policy file
# e.g. the processed form of "<friend><friend>d"
class Delegation:
    def __init__(self, relationship, delegator):
        self.relationship = relationship
        self.delegator = delegator

    def printDelegation():
        self.relationship.printStatement()
        print(delegator)

#to represent the processed form of a policy
class Policy:
    def __init__(self, statements):
        for statement in statements:
            if not (isinstance(statement, RelationshipStatement) or isinstance(statement, DelegationStatement) or isinstance(statement, Delegation)):
                raise TypeError("Policy class constructor must be passed an array of RelationshipStatement, DelegationStatement, and Delegation")
        self.statements = statements

    def printPolicy(self):
        for statement in self.statements:
            if(isinstance(statement, RelationshipStatement)):
                print("Relationship Statement\n-----------")
                statement.printStatement()
            elif(isinstance(statement, DelegationStatement)):
                print("Delegation Statement\n------------")
                statement.printStatement()
            else:
                print("Delegation:\n-----------")
                statement.printDelegation()

            print("\nOR\n")
