
def keibaLab_CourseTables(course):

    # 会場番号
    course_list = ['01:札幌', '02:函館', '03:福島', '04:新潟', '05:東京',
                   '06:中山', '07:中京', '08:京都', '09:阪神', '10:小倉']

    # 会場検索(例 course：京都 → '08:京都')
    course_list_in = [ course_out for course_out in course_list if course in course_out ]

    # 会場番号抽出(例 '08:京都' → '08')
    course_list_in = str(course_list_in)[2:4]
    # print(course_list_in)

    return course_list_in
