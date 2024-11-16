from tasks import task1, task2, task3

task = input("Enter the number of tasks you would: ")
if task == '1':
    print(task1.solve(input("Enter your string to find your number of smile: ")))
elif task == '2':
    print(task2.solve(input("Enter your string to find duplicated words: ")))
elif task == '3':
    print(task3.solve(input("Enter your string to find specific words: ")))