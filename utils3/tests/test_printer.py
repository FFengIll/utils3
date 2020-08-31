import traceback
import pytest
from utils3.data.printer import print_tree, Layout


class Employee:

    def __init__(self, fullname, function, head=None):
        self.team = []
        self.fullname = fullname
        self.function = function
        if head:
            head.team.append(self)

    def __str__(self):
        return self.function


@pytest.fixture()
def tree():
    # same type node
    jean = Employee("Jean Dupont", "CEO")
    isabelle = Employee("Isabelle Leblanc", "Sales", jean)
    enzo = Employee("Enzo Riviera", "Technology", jean)
    lola = Employee("Lola Monet", "RH", jean)
    kevin = Employee("Kevin Perez", "Developer", enzo)
    lydia = Employee("Lydia Petit", "Tester", enzo)

    # another type node
    lydia.team.append('UNKNOWN')
    return jean


def test_print_ud(tree):
    print_tree(tree, childattr="team", nameattr="fullname", layout=Layout.LR)
    print_tree(tree, childattr="team", nameattr="fullname", layout=Layout.UD)


if __name__ == "__main__":
    # same type node
    jean = Employee("Jean Dupont", "CEO")
    isabelle = Employee("Isabelle Leblanc", "Sales", jean)
    enzo = Employee("Enzo Riviera", "Technology", jean)
    lola = Employee("Lola Monet", "RH", jean)
    kevin = Employee("Kevin Perez", "Developer", enzo)
    lydia = Employee("Lydia Petit", "Tester", enzo)

    # another type node
    lydia.team.append('UNKNOWN')

    try:
        print_tree(jean, childattr="team", nameattr="fullname", layout='updown')
    except:
        traceback.print_exc()
