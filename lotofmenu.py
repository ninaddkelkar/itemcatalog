#!/usr/bin/env python
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from database_setup import Category, Base, Item, User

engine = create_engine('sqlite:///productcatalog.db?check_same_thread=False')
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


user1 = User(user_name="admin", email="admin@gmail.com")
session.add(user1)
session.commit()


# Category for Soccer
category1 = Category(name="Soccer")
session.add(category1)
session.commit()

item11 = Item(
    title="Two shinguards",
    description="Soccer shin guards are one of the most important pieces \
                of equipment you'll wear on the pitch.Soccer shin guards \
                are required for competition\
                by all organized leagues. This critical safety \
                piece is available \
                in slip-in, stirrup or shin-sock styles.",
    category=category1,
    user=user1)

item12 = Item(
    title="Shinguards",
    description="Dribble through defenders the way you were meant to. \
                The right pair of soccer shin guards eliminates cuts, \
                swelling and scrapes on the pitch, protecting your legs \
                so you can play your best.",
    category=category1,
    user=user1)

item13 = Item(
    title="Jersey",
    description="Whether you are a diehard soccer fan who never misses \
                 a match between rival countries or just enjoy repping \
                 your home nation while you travel abroad, you will \
                 appreciate high-quality international soccer clothing \
                 from this line.",
    category=category1,
    user=user1)

item14 = Item(
    title="Soccer Cleats",
    description="Soccer is a game played primarily by feet-and the right \
                cleats are the difference-making detail your game needs. \
                The latest soccer cleats and shoes deliver up agility, \
                traction and control, with a fit that lets you move \
                fluidly across any playing surface.",
    category=category1,
    user=user1)


session.add(item11)
session.add(item12)
session.add(item13)
session.add(item14)
session.commit()


# Category for BasketBall
category2 = Category(name="BasketBall")
session.add(category2)
session.commit()


# Category for BaseBall
category3 = Category(name="BaseBall")
session.add(category3)
session.commit()

item31 = Item(
    title="Bat",
    description="Discover industry-leading baseball bats crafted for \
                 playability. The latest generation of bats are designed \
                 with a performance-minded construction. From T-ball to \
                 senior league and beyond, discover the bat that's \
                 right for your game",
    category=category3,
    user=user1)
session.add(item31)
session.commit()

# Category for Frisbee
category4 = Category(name="Frisbee")
session.add(category4)
session.commit()

item41 = Item(
    title="Frisbee",
    description="A frisbee (also called a flying disc or simply a disc) \
                is a gliding toy or sporting item that is generally plastic \
                and roughly 20 to 25 centimetres (8 to 10 in) in diameter \
                with a pronounced lip. It is used recreationally and \
                competitively for throwing and catching, as \
                in flying disc games.",
    category=category4,
    user=user1)
session.add(item41)
session.commit()


# Category for Snowboarding
category5 = Category(name="Snowboarding")
session.add(category5)
session.commit()

item51 = Item(
    title="Googles",
    description="Snowboard goggles and ski goggles provide riders and \
                 skiers with eye protection from the elements such as \
                 bright sunlight, blowing snow and more. The best \
                 snowboard goggles should provide a comfortable \
                 fit with the right amount of tint for the \
                 weather conditions.",
    category=category5,
    user=user1)
session.add(item51)
session.commit()

item52 = Item(
    title="SnowBoard",
    description="Snowboards are boards where both feet are \
                secured to the same board, which are wider than \
                skis, with the ability to glide on snow. ",
    category=category5,
    user=user1)
session.add(item52)
session.commit()

# Category for RockClimbing
category6 = Category(name="Rockclimbing")
session.add(category6)
session.commit()


# Category for Foosball
category7 = Category(name="Foosball")
session.add(category7)
session.commit()


# Category for skating
category8 = Category(name="Skating")
session.add(category8)
session.commit()


# Category for Hockey
category8 = Category(name="Hockey")
session.add(category8)
session.commit()


item81 = Item(title="Stick", description="SA hockey stick is a \
              piece of sport equipment used by the players in \
              all the forms of hockey to move the ball or puck \
              (as appropriate to the type of hockey) either to \
              push, pull, hit, strike, flick, steer, launch or \
              stop the ball/puck during play with the objective \
              being to move the ball/puck around the playing area \
              and between team members using the stick, and to \
              ultimately score a goal with it against \
              an opposing team.", category=category8, user=user1)
session.add(item81)
session.commit()


"""
category2 = Category(name="BasketBall")
session.add(category2)
session.commit()

item21 = Item(title="", description="",category=category2)
session.add(item21)
session.commit()
"""

print "added  items for catalog!"
