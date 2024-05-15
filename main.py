from flask import Flask, jsonify, render_template, request
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import Integer, String, Boolean
from  sqlalchemy.sql.expression import func



app = Flask(__name__)

# CREATE DB
class Base(DeclarativeBase):
    pass
# Connect to Database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///cafes.db'
db = SQLAlchemy(model_class=Base)
db.init_app(app)


# Cafe TABLE Configuration
class Cafe(db.Model):
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(250), unique=True, nullable=False)
    map_url: Mapped[str] = mapped_column(String(500), nullable=False)
    img_url: Mapped[str] = mapped_column(String(500), nullable=False)
    location: Mapped[str] = mapped_column(String(250), nullable=False)
    seats: Mapped[str] = mapped_column(String(250), nullable=False)
    has_toilet: Mapped[bool] = mapped_column(Boolean, nullable=False)
    has_wifi: Mapped[bool] = mapped_column(Boolean, nullable=False)
    has_sockets: Mapped[bool] = mapped_column(Boolean, nullable=False)
    can_take_calls: Mapped[bool] = mapped_column(Boolean, nullable=False)
    coffee_price: Mapped[str] = mapped_column(String(250), nullable=True)

    def to_dict(self):
        return {
            "name": self.name,
            "map_url": self.map_url,
            "img_url": self.img_url,
            "location": self.location,
            "seats": self.seats,
            "has_toilet": self.has_toilet,
            "has_wifi": self.has_wifi,
            "has_sockets": self.has_sockets,
            "can_take_calls": self.can_take_calls,
            "coffee_price": self.coffee_price
        }

with app.app_context():
    db.create_all()

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/random",methods=["GET"])
def random():
    random_cafe=db.session.query(Cafe).order_by(func.random()).first()
    cafe_dict={
        "cafe":{
            "name": random_cafe.name,
            "map_url": random_cafe.map_url,
            "img_url": random_cafe.img_url,
            "location": random_cafe.location,
            "sesats": random_cafe.seats,
            "has_toilet": random_cafe.has_toilet,
            "has_wifi": random_cafe.has_wifi,
            "has_sockets": random_cafe.has_sockets,
            "can_take_calls": random_cafe.can_take_calls,
            "cofee_price": random_cafe.coffee_price
        }
    }
    return jsonify(cafe_dict)

@app.route("/all",methods=["GET"])
def all():
    result=db.session.execute(db.select(Cafe).order_by(Cafe.name))
    all_cafes=result.scalars().all()
    return jsonify(cafes=[cafe.to_dict() for cafe in all_cafes])

@app.route("/search")
def search():
    query_location = request.args.get("loc")
    result=db.session.execute(db.select(Cafe).where(Cafe.location==query_location))
    all_cafes=result.scalars().all()
    if all_cafes:
        return jsonify(cafes=[cafe.to_dict() for cafe in all_cafes])
    else:
        return jsonify("We couldn't find any cafe for this location")


@app.route("/add",methods=["POST","GET"])
def add():
    if request.method=="POST":
        cafe=Cafe(
            name=request.form.get("name"),
            map_url=request.form.get("map_url"),
            img_url=request.form.get("img_url"),
            location=request.form.get("location"),
            seats=request.form.get("seats"),
            has_toilet=bool(request.form.get("has_toilet")),
            has_wifi=bool(request.form.get("has_wifi")),
            has_sockets=bool(request.form.get("has_sockets")),
            can_take_calls=bool(request.form.get("can_take_calls")),
            coffee_price=str(request.form.get("cofee_price")),
        )
        db.session.add(cafe)
        db.session.commit()
        response={"response":{
            "success":"Successfully added the new cafe"
        }}
        return jsonify(response)
    return jsonify("something went wrong.")

@app.route("/update/<int:cafe_id>",methods=["PATCH"])
def update_price(cafe_id):
    chosen_cafe=db.session.get(Cafe,cafe_id)
    if chosen_cafe:
        chosen_cafe.coffee_price=request.args.get("new_price")
        db.session.commit()
        return jsonify(response={"Success":"Changed Price Successfully"}),202
    else:
        return jsonify(error={"Not Found":"Couldn't change price"}), 404

@app.route("/delete/<int:cafe_id>",methods=["DELETE"])
def delete_cafe(cafe_id):
    api_key=request.args.get("api_key")
    if api_key=="123":
        closed_cafe=db.session.get(Cafe,cafe_id)
        if closed_cafe:
            db.session.delete(closed_cafe)
            db.session.commit()
            return jsonify(response={"Success":"You are successfully deleted Cafe"}),200
        else:
            return jsonify(error={"Not Found Cafe":"You couldn't deleted Cafe"}),404
    else:
        return jsonify(error={"Not Found Api Key":"Please Check Your Api Key"}),403

# HTTP GET - Read Record

# HTTP POST - Create Record

# HTTP PUT/PATCH - Update Record

# HTTP DELETE - Delete Record


if __name__ == '__main__':
    app.run(debug=True)
