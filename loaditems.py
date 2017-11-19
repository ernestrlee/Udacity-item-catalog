from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from database_setup import Base, User, Category, Item

engine = create_engine('sqlite:///cataloginfo.db')
# Bind the engine to the metadata of the Base class so that the
# declaratives can be accessed through a DBSession instance
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
# A DBSession() instance establishes all conversations with the database
# and represents a "staging zone" for all the objects loaded into the
# database session object. Any change made against the objects in the
# session won't be persisted into the database until you call
# session.commit(). If you're not happy about the changes, you can
# revert all of them back to the last commit by calling
# session.rollback()
session = DBSession()

# Create a user
User1 = User(name="Sammy Gee", email="sammy.gee@us.com",
             picture='https://i.redd.it/fnf14eb7thsz.gif')
session.add(User1)
session.commit()

# Add initial categories and items to the database
category1 = Category(name="Soccer")

session.add(category1)
session.commit()

Item1 = Item(user_id=1,
             name="Soccer ball",
             description="A black and white ball with hexagons.",
             imageurl=("https://upload.wikimedia.org/wikipedia/en/thumb/e/ec/Soccer_ball.svg/600px-Soccer_ball.svg.png"),
             category=category1)

session.add(Item1)
session.commit()

Item2 = Item(user_id=1,
             name="Socks",
             description="Long decorative tube socks that come in multiple colors.",
             imageurl="https://fgl.scene7.com/is/image/FGLSportsLtd/331951554_30_a",
             category=category1)

session.add(Item2)
session.commit()

category2 = Category(name="Basketball")

session.add(category2)
session.commit()

Item1 = Item(user_id=1,
             name="Jersey",
             description="A sleeveless shirt that comes in multiple colors with numbers on it.",
             imageurl="http://nba.frgimages.com/FFImage/thumb.aspx?i=/productImages%2f_1741000%2fff_1741475_xl.jpg",
             category=category2)

session.add(Item1)
session.commit()

Item2 = Item(user_id=1,
             name="Basketball",
             description="An orange ball with black lines.",
             imageurl="http://a.espncdn.com/combiner/i?img=/redesign/assets/img/icons/ESPN-icon-basketball.png",
             category=category2)

session.add(Item2)
session.commit()

category3 = Category(name="Baseball")

session.add(category3)
session.commit()

Item1 = Item(user_id=1,
             name="Baseball",
             description="A white ball with red laces.",
             imageurl="https://upload.wikimedia.org/wikipedia/en/thumb/1/1e/Baseball_%28crop%29.jpg/290px-Baseball_%28crop%29.jpg",
             category=category3)

session.add(Item1)
session.commit()

category4 = Category(name="Frisbee")

session.add(category4)
session.commit()

category5 = Category(name="Snowboarding")

session.add(category5)
session.commit()

category6 = Category(name="Rock Climbing")

session.add(category6)
session.commit()

category7 = Category(name="Foosball")

session.add(category7)
session.commit()

Item1 = Item(user_id=1,
             name="Foosball table",
             description="A large table with men attached to sticks.",
             imageurl="https://upload.wikimedia.org/wikipedia/commons/thumb/e/e5/Foosball11Players.jpg/220px-Foosball11Players.jpg",
             category=category7)

session.add(Item1)
session.commit()

category8 = Category(name="Skating")

session.add(category8)
session.commit()

category9 = Category(name="Hockey")

session.add(category9)
session.commit()


print "added items!"
