# COllect email from user, split from @ with domain & name

def main():
    print(" Welcome to the email slicer ")
    print(" ")

    email_input = input(" Input your Email Address: ")

    (username, domain) = email_input.split("@")
    (domain, extension) = domain.split(".")

    print("username : ", username)
    print("Domain :", domain)
    print("extension: ", extension)

while True:
    main()