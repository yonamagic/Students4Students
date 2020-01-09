class User:
    def __init__(self, name, strong_subjects, weak_subjects):
        self.name = name
        self.strong_subjects = strong_subjects
        self.weak_subjects = weak_subjects

    def get_strong_subjects_as_string(self):
        ret_string = ''
        for sub in self.strong_subjects:
            ret_string = ret_string + sub.name + ','
        return ret_string

