from collections import namedtuple

if __name__ == "__main__":
    n = int(input())
    heading = input().split()
    # print(heading)
    student = namedtuple('STUDENT',f'{heading[0]} {heading[1]} {heading[2]} {heading[3]}')
    s = 0
    for _ in range(n):
        data = input().split()
        # print(data)
        st = student(data[0],data[1],data[2], data[3])
        s = s + int(st.MARKS)
    print(f"{s/n:.2f}")