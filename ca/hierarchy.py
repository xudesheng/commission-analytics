import sys
import pandas as pd

sys.path.append(".")

try:
    from . import salesman
except:
    import salesman


class Hierarchy:
    def __init__(self):
        self.__emp_list = {}  # emp_no: salesman
        self.__top_emp = None
        self.__vp_list = []
        self.__position = {}  # emp_no: "x,y"

    def get_base_position(self):
        '''
        this function should be replaced by class mothod in casession class.
        :return:
        '''
        page_left_margin = 0.2
        block_width = 4.0
        block_w_gap = 3.0
        page_bottom_margin = 0.2
        block_height = 1.0
        block_h_gap = 0.4

        return page_left_margin, block_width, block_w_gap, page_bottom_margin, block_height, block_h_gap

    def generate_position(self):
        self.__position = {}  # clean data
        # page_left_margin = 0.2
        # block_width = 1.6
        # block_w_gap = 0.2
        # page_bottom_margin = 0.2
        # block_height = 1.0
        # block_h_gap = 0.2

        page_left_margin, block_width, block_w_gap, page_bottom_margin, block_height, block_h_gap = self.get_base_position()

        if not self.__top_emp:
            self.validate_emp_list()
            raise ValueError(
                "Can't find top boss in hierarchy!")  # if no top boss, then width and depth can't be calculated.
        top_boss = self.__emp_list.get(self.__top_emp, None)
        if not top_boss:
            raise ValueError("Can't find top boss based emp no!")

        self.setup_child_position(1, 0, top_boss, 0, )

        return self.__position

    def setup_child_position(self, current_level, current_height, current_node, leaves_count):
        '''
        this is a recursive call to setup a position of each block.
        deep search first.

        :param current_level:
        :param current_sibling:
        :param current_node:
        :return:
        '''
        page_left_margin, block_width, block_w_gap, page_bottom_margin, block_height, block_h_gap = self.get_base_position()

        max_height = 0.0
        min_height = -1

        reporters = current_node.get_reporters()
        if len(reporters) == 0:  # this is a leaf
            cx = page_left_margin + (current_level - 1) * (block_w_gap + block_width)
            cy = page_bottom_margin + leaves_count * (block_h_gap + block_height)
            self.__position[current_node.get_emp_no()] = "%f,%f" % (cx, cy)
            leaves_count += 1
            return current_level, cy, leaves_count
        else:  # has child
            for emp_no in reporters:
                reporter = self.__emp_list.get(emp_no, None)
                if not reporter:
                    raise ValueError("%s can't be found in setup_child_position()" % emp_no)

                _, current_height, leaves_count = self.setup_child_position(current_level + 1, current_height, reporter,
                                                                            leaves_count, )
                if min_height < 0.0:
                    min_height = current_height
                elif current_height < min_height:
                    min_height = current_height

                if current_height > max_height:
                    max_height = current_height

        cx = page_left_margin + (current_level - 1) * (block_w_gap + block_width)
        cy = (max_height + min_height) / 2.0

        self.__position[current_node.get_emp_no()] = "%f,%f" % (cx, cy)

        return current_level, cy, leaves_count

    def get_depth_width(self):
        if not self.__top_emp:
            return 0, 0  # if no top boss, then width and depth can't be calculated.
        top_boss = self.__emp_list.get(self.__top_emp, None)
        if not top_boss:
            raise ValueError("Can't find top boss based emp no!")

        width = 1
        depth = 1
        reporters = top_boss.get_reporters()
        if len(reporters) == 0:
            return width, depth  # only one, return 1,1

        depth = self.get_depth(depth, top_boss)
        width = self.get_width(0, top_boss)

        return width, depth

    def get_width(self, current_width, current_node):
        '''
        this is a recursive call to get width of a tree
        it's a total of all leaves.
        :param current_width:
        :param current_node:
        :return:
        '''

        if not current_node:
            raise ValueError("current node in get_width() should a salesman object!")

        reporters = current_node.get_reporters()
        for emp_no in reporters:
            reporter = self.__emp_list.get(emp_no, None)
            if not reporter:
                raise ValueError("%s can't be found in get_width()" % emp_no)

            if len(reporter.get_reporters()) == 0:
                current_width += 1
            else:
                current_width = self.get_width(current_width, reporter)

        return current_width

    def get_depth(self, current_depth, current_node):
        '''
        this is a recursive call to get depth of a tree
        :param current_depth:
        :param current_node: salesman object
        :return:
        '''
        if not current_node:
            raise ValueError("current node in get_depth() should be a valid salesman object!")

        reporters = current_node.get_reporters()
        if len(reporters) == 0:
            return current_depth
        else:
            current_depth += 1
            max_depth = current_depth

            for emp_no in reporters:
                reporter = self.__emp_list.get(emp_no, None)
                if not reporter:
                    raise ValueError("Error in get_depth() when find child object!")

                new_depth = self.get_depth(current_depth, reporter)
                if new_depth > max_depth:
                    max_depth = new_depth

            return max_depth

    def get_top_emp(self):
        return self.__top_emp

    def get_emp_list(self):
        return self.__emp_list

    def collect_reporters(self, new_salesman):
        '''
        collect reporters from existing emp list by checking who's boss is current user.
        :param new_salesman:
        :return:
        '''
        future_reporters = []
        for emp_no, emp in self.__emp_list.iteritems():
            existing_boss = emp.get_current_boss()
            if existing_boss:
                if existing_boss == new_salesman.get_emp_no():
                    future_reporters.append(emp_no)
                    # print(future_reporters)

        return future_reporters

    def get_multiple_sales_allbosses(self, emp_list, existing_bosses=None):
        '''
        get all uplevel managers from a list of sales
        :param emp_list:
        :param existing_bosses: initialiy it's blank, it will include existing managers in recursive call.
        :return:
        '''
        boss_list = []
        for emp in emp_list:
            current_sales = self.__emp_list.get("%d" % emp, None)
            if not current_sales:
                raise ValueError("get_multiple_sales_allbosses met a sales with wrong ID:%s" % emp)

            current_bosses = current_sales.get_boss()
            if len(current_bosses) > 0:  # indeed, ony first one will be deal with
                his_boss = current_bosses[0]
                if not his_boss:
                    return boss_list

                his_boss_int = int(his_boss)

                # print("Sales:%s->Manager:%s" % (emp, his_boss_int))

                if existing_bosses and (not his_boss_int in existing_bosses):
                    boss_list.append(his_boss_int)
                    boss_list.extend(self.get_multiple_sales_allbosses([his_boss_int], boss_list))
                elif not existing_bosses and (not his_boss_int in boss_list):
                    boss_list.append(his_boss_int)
                    boss_list.extend(self.get_multiple_sales_allbosses([his_boss_int], boss_list))

        return boss_list

    def get_salesman_allbosses(self, existing_salesman):
        '''
        return a list of all level of boss of this sales man.
        :param existing_salesman:
        :return: manager in object
        '''
        boss_list = []
        current_bosses = existing_salesman.get_boss()
        if len(current_bosses) > 0:
            boss_list.extend(current_bosses)
            uplevel_boss = self.__emp_list.get(current_bosses[0], None)
            if uplevel_boss:
                #boss_list.append(uplevel_boss)
                uplevel_boss_list = self.get_salesman_allbosses(uplevel_boss)
                boss_list.extend(uplevel_boss_list)
        return boss_list

    def get_all_lowest_reporters(self, manager):
        '''
        bypass middle level manager and return all lowest level sales rep for a manager.
        :param manager:
        :return: emp_no list
        '''
        reporters_list = []
        current_reporters = manager.get_reporters()
        for reporter in current_reporters:
            next_salesman = self.__emp_list.get(reporter, None)
            if next_salesman:
                if not next_salesman.is_manager():
                    reporters_list.append(reporter)
                else:
                    reporters_list.extend(self.get_all_lowest_reporters(next_salesman))
        return reporters_list

    def get_all_reporters_and_selfobj(self, managerkey):
        manager = self.__emp_list.get("%d" % managerkey, None)
        if not manager:
            raise ValueError("Can't found %s in manager list!" % managerkey)
        return self.get_all_reporters_and_self(manager)

    def get_all_reporters_and_self(self, manager):
        '''
        get all low level reporters and managers and himself in one list
        :param manager:
        :return: object list
        '''
        reporters_list = []
        reporters_list.append(manager)  # add him_self
        current_reporters = manager.get_reporters()
        for reporter in current_reporters:
            next_salesman = self.__emp_list.get(reporter, None)
            if next_salesman:
                if not next_salesman.is_manager():
                    reporters_list.append(next_salesman)
                else:
                    reporters_list.extend(self.get_all_reporters_and_self(next_salesman))
        return reporters_list

    def get_sales_allreporters(self, existing_salesman):
        '''
        return all children reporters from current salesman
        :param existing_salesman:
        :return: emp_no list
        '''
        reporters_list = []
        current_reporters = existing_salesman.get_reporters()
        reporters_list.extend(current_reporters)
        for reporter in current_reporters:
            next_salesman = self.__emp_list.get(reporter, None)
            if next_salesman:
                reporters_list.extend(self.get_sales_allreporters(next_salesman))
        return reporters_list

    def validate_emp_list(self):
        # print(self.__emp_list)
        print("\nStart to validate hierarchy data...")
        issue_no_list = []
        for emp_no, emp in self.__emp_list.iteritems():
            # print(emp)
            current_boss_list = emp.get_boss()
            if len(current_boss_list) == 0:
                print("\tEMP_NO:(%s) may be the top boss since it does't have boss!" % emp_no)
            else:
                existing_boss = self.__emp_list.get(current_boss_list[0], None)  # only pickup first one.
                if not existing_boss:
                    print("\tEMP_NO:(%s) may have data issue since it doesn't have boss!" %
                          (unicode(emp_no, errors='replace')))
                    #print(emp)
                    if not current_boss_list[0] in issue_no_list:
                        issue_no_list.append(current_boss_list[0])
            try:
                emp_no_int = int(emp_no)
            except:
                print("\tEmployee No:%s is not an integer number!" % emp_no)
                issue_no_list.append(emp_no)

        if len(issue_no_list) > 0:
            print("\n\n\tSummary of missing info sales or manager:")
            print(issue_no_list)
            print("\n\n")
            raise ValueError("Hierarchy has issue, please resolve it before continue!")
        else:
            print("\tNo issue found in hierarchy data!")

    def add_salesman(self, new_salesman):
        '''
        add a new sales man to emp_list but this function will perform recursve check.
        :param new_salesman:
        :return:
        '''
        if new_salesman.get_emp_no() in self.__emp_list.keys():  # if already exists, then do nothing
            return

        existing_reporters = self.collect_reporters(new_salesman)  # search existing reporters in list
        new_salesman.add_reporters(existing_reporters)  # add as current reporters

        # check current all reporters are not any level of managers.
        all_bosses = self.get_salesman_allbosses(new_salesman)
        if new_salesman.get_emp_no() in all_bosses:
            raise ValueError("Current Hierarchy up level has same emp_no:" + new_salesman.get_emp_no())

        all_reporters = self.get_sales_allreporters(new_salesman)
        if new_salesman.get_emp_no() in all_reporters:
            raise ValueError("Current Hierarchy low level has same emp_no:" + new_salesman.get_emp_no())

        # add current node
        self.__emp_list[new_salesman.get_emp_no()] = new_salesman

        # sync manager node
        current_boss_list = new_salesman.get_boss()
        if len(current_boss_list) == 0:
            # this is top boss
            self.__top_emp = new_salesman.get_emp_no()
        else:
            existing_boss = self.__emp_list.get(current_boss_list[0], None)  # only pickup first one.
            if existing_boss:
                if not (new_salesman.get_emp_no() in existing_boss.get_reporters()):
                    existing_boss.add_reporters([new_salesman.get_emp_no()])

        # sync reporters role.
                    # current_reporters_list = new_salesman.get_reporters()
                    # for emp_no in current_reporters_list:
                    #    reporter = self.__emp_list.get(emp_no, None)
                    #    if reporter:
                    # reporter.set_boss(emp_no)  # find a bug, boss can't be setup correctly
                    #        reporter.set_boss(new_salesman.get_emp_no())


def build_hierarchy_from_csv(csvfile):
    df = pd.read_csv(csvfile, index_col='EMPLOYEE NO',
                     dtype={'EMPLOYEE NO': object, 'MANAGER': object, 'Status': object, 'Multiplier': object})
    #print(df)

    new_h = Hierarchy()
    for index, row in df.iterrows():
        if index == 91661: print index, row['NAME'], row['Multiplier']
        new_sales = salesman.Salesman(str(index), row['NAME'],
                                      str(row['Status'],
                                          str(row['Multiplier'])))  # index has to be converted to string.
        if pd.notnull(row['MANAGER']):
            new_sales.set_boss(row['MANAGER'])

        new_h.add_salesman(new_sales)

    return new_h


def build_hierarchy_from_sample():
    '''
        EMPLOYEE NO	NAME	MANAGER
    1001	Jim H
    1002	Richard Shou	1001
    1003	Matt Cohen	1001
    1004	Carlos D	1003
    1005	Sanjay V	1003
    1006	Michal P	1003
    1007	Chris M	1006
    1008	Elric F	1006
    1009	Zhang J	1002
        :return:
        '''
    new_h = Hierarchy()

    jimh = salesman.Salesman('1001', 'Jim H')

    richardshou = salesman.Salesman('1002', 'Richard Shou')
    richardshou.set_boss('1001')

    mattc = salesman.Salesman('1003', 'Matt Cohen')
    mattc.set_boss('1001')

    carlosd = salesman.Salesman('1004', 'Carlos D')
    carlosd.set_boss('1003')

    sanjayv = salesman.Salesman('1005', 'Sanjay V')
    sanjayv.set_boss('1003')

    michaelp = salesman.Salesman('1006', 'Michael P')
    michaelp.set_boss('1003')

    chrism = salesman.Salesman('1007', 'Chris M')
    chrism.set_boss('1006')

    elricf = salesman.Salesman('1008', 'Elric F')
    elricf.set_boss('1006')

    zhangj = salesman.Salesman('1009', 'Zhang J')
    zhangj.set_boss('1002')

    new_h.add_salesman(jimh)
    new_h.add_salesman(richardshou)
    new_h.add_salesman(mattc)
    new_h.add_salesman(carlosd)
    new_h.add_salesman(sanjayv)
    new_h.add_salesman(michaelp)
    new_h.add_salesman(chrism)
    new_h.add_salesman(elricf)
    new_h.add_salesman(zhangj)

    return new_h


def main():
    # new_h = build_hierarchy_from_sample()
    new_h = build_hierarchy_from_csv('../Sample/FY16Q3/FY16Q3-Hierarchy.csv')

    top_emp = new_h.get_top_emp()
    if top_emp:
        print("Biggest Boss is:" + top_emp + "\n")
    else:
        print("can't find top boss!\n")

    for emp_no, sales in new_h.get_emp_list().iteritems():
        print("EMP:%s\t%s" % (emp_no, sales))

    # width, depth = new_h.get_depth_width()
    # print("Width:%d, \tDepth:%d\n" % (width, depth))

    position = new_h.generate_position()
    print(position)

if __name__ == "__main__":
    main()
