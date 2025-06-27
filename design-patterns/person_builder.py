from models.person import Person


class PersonBuilder:
    def __init__(self):
        self.person = Person()

    def named(self, name):
        self.person.name = name
        return self

    def aged(self, age):
        self.person.age = age
        return self


    def build(self):
        return self.person