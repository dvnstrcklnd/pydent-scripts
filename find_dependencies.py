import re
import argparse
from util.pydent_helper import create_session

def main():
    args = get_args()
    session = create_session(args.aq_instance)

    plan = session.Plan.find(args.plan_id)
    operations = plan.operations
    operation_types = get_operation_types(session, operations)
    dependencies = get_dependencies(session, operation_types)

    for d in dependencies:
        print(d)

def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("-p", "--plan_id",
                        help="ID of Aquarium Plan to take Operations from")
    parser.add_argument("-i", "--aq_instance",
                        help="Instance of Aquarium search on")
    return parser.parse_args()

def get_operation_types(session, operations):
    ot_ids = [o.operation_type_id for o in operations]
    operation_types = session.OperationType.find(ot_ids)
    return operation_types

def get_dependencies(session, operation_types):
    found = []
    unopened = []

    for ot in operation_types:
        unopened.append((ot.category, ot.name))

    unopened = list(set(unopened))

    pattern = re.compile(r'^\s*needs\s+[\"\'](.+)\/(.+)[\"\']')

    while unopened:
        names = [n[1] for n in unopened]
        found += unopened
        unopened = []

        operation_types = session.OperationType.where({"name": names})
        contents = [ot.protocol.content for ot in operation_types]

        libraries = session.Library.where({"name": names})
        contents += [library.source.content for library in libraries]

        for content in contents:
            lines = content.split("\n")

            for l in lines:
                match = re.search(pattern, l)
                if not match: continue
                need = (match.group(1), match.group(2))
                unopened.append(need)

    return sorted(list(set(found)))

if __name__ == "__main__":
    main()
