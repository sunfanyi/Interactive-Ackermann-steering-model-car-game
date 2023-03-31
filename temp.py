class Apple:
    a = 1

    def show(self):
        print(self.a)


apple1 = Apple()
apple2 = Apple()

# print(apple1.a)

apple1.show()
Apple.a = 3
apple1.show()
apple2.show()
