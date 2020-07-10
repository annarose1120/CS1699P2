#to represent the processed form of a relationship statement from the policy file
#Ex. processed form of <friend><parent>a(rwx)
#syntax must have been verified beforehand
class relationshipStatement:
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
class delegationStatement:
    def __init__(self, relationship):
        self.relationship = relationship

    def printStatement(self):
        self.relationship.printStatement()

class policy:
    def __init__(self, statements):
        for statement in statements:
            if not (isinstance(statement, relationshipStatement) or isinstance(statement, delegationStatement)):
                raise Error("policy class given wrong type of objects")
        self.statements = statements
