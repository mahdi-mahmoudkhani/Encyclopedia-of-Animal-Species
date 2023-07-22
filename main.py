import regex as re
from treelib import Tree
from treelib.exceptions import NodeIDAbsentError


class GroupAlreadyExistsException(Exception):
    pass


class NoSuchSuperSetException(Exception):
    pass


class Group:

    _treeDiagram = Tree()
    _treeDiagram.create_node(tag = "Tree Of Life", identifier="0")
    _tree = {}
    _instances = {}

    def __init__(self, type: str, name: str, superSet: tuple = None, info: str = None, attributes : dict = None) -> None:
        """
        Initializing the instance

        - Args:
            - type (str): Type of the group. e.g. Life, Kingdom, Genus
            - name (str): Name of the group
            - superSet (tuple, optional): Super Set of the group that comes in a tuple with the - - format (type, name). it is optional in case the type of the group entered is Life and there is no super set
            - info (str, optional): A brief info of the group
            - attributes (dictionary, optional): Main attributes of the group
        """

        if (type, name) in self._tree.keys():
            raise GroupAlreadyExistsException
        if type != "Life":
            if superSet == None:
                raise NoSuchSuperSetException
            try:
                self._tree[superSet].append((type, name))
            except KeyError:
                raise NoSuchSuperSetException
        self._tree.update({(type, name): []})
        self.type = type
        self.name = name
        self.superSet = superSet
        self._info = info
        self.attributes = attributes
        self.attributes = self.completeAttr(self)
        self._instances.update({(type, name): self})
        if type == "Life":
            Group._treeDiagram.create_node(
                tag=f"{self.name} ({self.type})", identifier=f"{self.type} {self.name}", parent="0")
        else:
            Group._treeDiagram.create_node(
                tag=f"{self.name} ({self.type})", identifier=f"{self.type} {self.name}", parent=f"{superSet[0]} {superSet[1]}")

    def completeAttr(self, start):
        def subfunc(start: Group) -> dict:
            attr = {}
            if start.superSet != None:
                upperAttr = subfunc(self._instances[start.superSet])
                if upperAttr:
                    attr.update(upperAttr)
            if start.attributes:
                attr.update(start.attributes)
            return attr
        return subfunc(start)

    @property
    def info(self) -> str:
        """
        Returns the information of the group including the name, its super group, a brief info, and the given attributes.

        - Returns:
            - str: A string in the format of a dict containing the info.
        """
        tempResult = f"--{self.type}{'-'*(28-len(self.type))}\nName: {self.name},"
        if self.superSet:
            tempResult += f"\nSuper Group: {self.superSet[0]},"
        if self._info:
            tempResult += f"\nBrief Info: {self._info},"
        for key, value in self.attributes.items():
            tempResult += f"\n{key}: {value},"
        return tempResult[::-1].replace(',', '.', 1)[::-1]

    @info.setter
    def info(self, newData : tuple):
        def changeSubBranch(branch: Group | Species):
            if self.type != "Species":
                for branch in self._tree[(branch.type, branch.name)]:
                    changeSubBranch(self._instances[branch])
            branch.attributes.update({newData[0]: newData[1]})

    @classmethod
    def delete(cls, type: str, name: str) -> None:
        """
        Deletes the given group and all of its subbranches.

        - Args:
            - type (str): Type of the group. e.g. Life, Kingdom, Genus
            - name (str): Name of the group
        """
        try:
            cls._treeDiagram.remove_node(f"{type} {name}")
        except NodeIDAbsentError:
            pass
        if type != "Life":
            superSet = cls._instances[(type, name)].superSet
            cls._tree[superSet].remove((type, name))
        if type == "Species":
            cls._instances.pop((type, name))
            return

        for type_sub, name_sub in cls._tree[(type, name)].copy():
            cls.delete(type_sub, name_sub)
        cls._instances.pop((type, name))
        cls._tree.pop((type, name))

    @property
    def tree(self) -> dict:
        """
        Returns the tree starting from the instance group.

        - Returns:
            - dict: A dictionary containing every sub-group which is a subbranch of the group keyed by their supers.
        """
        def completeTree(start : tuple) -> dict:
            try:
                tempDict = {start: self._tree[start]}
                for group in self._tree[start]:
                    tempDict.update(completeTree(group))
                return tempDict
            except KeyError:  # occurs when we reach a species
                return dict()

        if self.type == "Life":
            return self._tree
        elif self.type == "Species":
            return {(self.type, self.name): None}
        else:
            for key, value in self._tree.items():
                if key[0] == self.type and key[1] == self.name:
                    return completeTree(key)

    @classmethod
    def fullTreeView(cls) -> Tree:
        """
        Returns the full tree view

        - Returns:
            - Tree: an instance of he Tree class
        """
        return cls._treeDiagram

    @property
    def subTreeView(self) -> Tree:
        """
        Returns the tree view from the instance group

        - Returns:
            - Tree: an instance of he Tree class
        """
        return self._treeDiagram.subtree(f"{self.type} {self.name}")


    @classmethod
    def advancedSearch(cls, superSet: str = "", query: str = "", match_type: str = "", filters: dict = None) -> dict:
        """
        Searches for instances that match the given query and filters, optionally restricted to a specific superSet.

        - Args:
            - superSet (str, optional): The superSet to search within. Defaults to None (search all superSets).
            - query (str, optional): The search query. Defaults to None (search all types and names).
            - match_type (str, optional): The match type to use for the query. Can be "inclusive" (default), "exact", or "regular expression".
            - filters (dict, optional): A dictionary of filters to apply. Each key should be an attribute name, and each value should be a tuple of (operator, value), where operator is one of "exact", "range", "lt" (less than), "lte" (less than or equal to), "gt" (greater than), or "gte" (greater than or equal to), and value is the value to compare against. Defaults to None (no filters applied).

        - Returns:
            - dict: A dictionary containing the matching instances, keyed by their (type, name) tuples.
        """
        matches = {}
        for (type, name), instance in cls._instances.items():
            if superSet != "":
                if instance.superSet != superSet:
                    continue

            if query != "":
                if match_type == "inclusive":
                    if query.lower() not in instance.type.lower() and query.lower() not in instance.name.lower():
                        continue
                elif match_type == "exact":
                    if query != instance.type and query != instance.name:
                        continue
                elif match_type == "regular expression":
                    try:
                        pattern = re.compile(query, re.IGNORECASE)
                    except re.error as e:
                        print(f"Regular expression error: {e}")
                        continue
                    try:
                        type_search = pattern.search(instance.type).group()
                    except AttributeError:
                        type_search = None

                    try:
                        name_search = pattern.search(instance.name).group()
                    except AttributeError:
                        name_search = None

                    if type_search != instance.type and name_search != instance.name:
                        continue
                else:
                    raise ValueError(
                        f"Invalid match_type: {match_type}. Must be 'inclusive', 'exact', or 'regular expression'.")

            if filters is not None and filters != {}:
                match_all_filters = True
                for attr, (op, value) in filters.items():
                    if attr not in instance.attributes:
                        match_all_filters = False
                        break

                    attr_value = instance.attributes[attr]
                    if op == "exact":
                        if not isinstance(attr_value, str):
                            match_all_filters = False
                            break
                        if value.lower() != attr_value.lower():
                            match_all_filters = False
                            break
                    elif op == "range" and not (value[0] <= attr_value <= value[1]):
                        match_all_filters = False
                        break
                    elif op == "lt" and not (attr_value < value):
                        match_all_filters = False
                        break
                    elif op == "lte" and not (attr_value <= value):
                        match_all_filters = False
                        break
                    elif op == "gt" and not (attr_value > value):
                        match_all_filters = False
                        break
                    elif op == "gte" and not (attr_value >= value):
                        match_all_filters = False
                        break

                if match_all_filters:
                    matches[(type, name)] = instance
            else:
                matches[(type, name)] = instance

        return matches
    
    
    def createNew(line : str):
        type = re.search(r'type=\"(.*?)\"', line).group(1)
        name = re.search(r'name=\"(.*?)\"', line).group(1)
        superSet = extraAttr = info = superSetName = superSetType = str()
        finalAttr = {}
        try:
            superSet = re.search(r'superSet=\((.*?)\)', line).group(1)
        except AttributeError:
            superSet = None
        try:
            info = re.search(r'info=\"(.*?)\"', line).group(1)
        except AttributeError:
            info = None
        try:
            extraAttr = re.search(r'extraAttr=\((.*?)\)', line.replace(' ', '')).group(1)
            for i in range (extraAttr.count("=")):
                equalSign = extraAttr.find("=")
                commaSign = extraAttr.find(",")
                attrKey = extraAttr[:equalSign]
                if extraAttr[equalSign + 1] == '"':
                    attrValue = extraAttr[equalSign +2: commaSign]
                    finalAttr[attrKey] = attrValue
                else:
                    attrValue = extraAttr[equalSign +1: commaSign]
                    finalAttr[attrKey] = float(attrValue)
                extraAttr = extraAttr[extraAttr.find(",") +1 :]
        except AttributeError:
            extraAttr = None

        if type == "Species":
            age = re.search(r'age=(.*?)\,', line.replace(' ', '')).group(1)
            weigth = re.search(r'weight=(.*?)\,',
                                line.replace(' ', '')).group(1)
            size = re.search(
                r'size=(.*?)\,', line.replace(' ', '')).group(1)
            superSetType = superSet[:superSet.find(',')]
            superSetName = superSet[superSet.find(',') + 2:]
            Species(name=name, superSet=(superSetType[1:-1], superSetName[1:-1]),
                    age=age, weight=weigth, size=size, info=info, attributes=finalAttr)

        elif type == "Life":
            Group(type="Life", name=name, info=info, attributes=finalAttr)
        else:
            superSetType = superSet[:superSet.find(',')]
            superSetName = superSet[superSet.find(',') + 2:]
            Group(type=type, name=name, superSet=(superSetType[1:-1], superSetName[1:-1]), info=info, attributes=finalAttr)



    @classmethod
    def readFromFile(cls,fileName : str) -> None:
        f = open(fileName, 'rt')
        for line in list(f.readlines()):
            cls.createNew(line = line)

class Species(Group):


    def __init__(self, name: str, superSet: tuple, age: int | float, weight: int | float, size: int | float, info: str, attributes : dict = None) -> None:
        """
        Initializing the instance

        - Args:
            - name (str): Name of the group
            - superSet (tuple): Super Set of the group that comes in a tuple with the -format (type, name). it is optional in case the type of the group entered is Life and there is no super set
            - age (int or float): Average age of the species
            - weight (int or float): Average weight of the species
            - size (int or float): Average size of the species
            - info (str): A brief info of the group
            - attributes (dictionary, optional): Main attributes of the group
        """

        if (type, name) in self._tree.keys():
            raise GroupAlreadyExistsException
        if superSet == None:
            raise NoSuchSuperSetException
        try:
            self._tree[superSet].append(("Species", name))
        except KeyError:
            raise NoSuchSuperSetException
        self._instances.update({("Species", name): self})
        self.name = name
        self.type = "Species"
        self.superSet = superSet
        self._info = info
        self.attributes = {
            "Age": age,
            "Weight": weight,
            "Size": size
        }
        self.attributes.update(attributes)
        self.attributes = self.completeAttr(self)
        Group._treeDiagram.create_node(
            tag=f"{self.name} ({self.type})", identifier=f"{self.type} {self.name}", parent=f"{superSet[0]} {superSet[1]}")

    def completeAttr(self, start):
        def subfunc(start: Group) -> dict:
            attr = {}
            if start.superSet != None:
                upperAttr = subfunc(self._instances[start.superSet])
                if upperAttr:
                    attr.update(upperAttr)
            if start.attributes:
                attr.update(start.attributes)
            return attr
        return subfunc(start)