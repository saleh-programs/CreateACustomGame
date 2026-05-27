
import "../../styles/Dashboard.css"
import whiteboard from "../assets/whiteboard.png"
import { Link } from "react-router-dom";
function Dashboard(){

    return (
    <div
    style={{
        width: "100%",
        height: "100%",
        background: "linear-gradient(brown,red)",
        display: "flex",
        justifyContent: "center",
        alignItems: "center",
        flexDirection: "column"
    }}>
        <h1 style={{
            fontSize: "2.5rem",
            color: "white", 
            fontWeight: "bold",
        }}>
            Let's create a game!
        </h1>

        <section
        style={{
            width: "400px",
            height: "400px",
            backgroundColor: "white",
            borderRadius: "10px",
            boxShadow: "0 0 40px 10px white",
            display: "flex",
            flexDirection: "column",
        }}>

            <section>
                <img style={{width: "100%"}} src={whiteboard} alt="" />
            </section>
            <section style={{
                width: "100%",
                display: "flex",
                justifyContent: "center"
            }}>
                  <Link
                    to="/create"
                  >
                    <button id={"startButton"} style={{
                        borderRadius: "10px",
                        padding: "10px 20px",
                        fontSize: "30px",
                        fontWeight: "bold"
                    }}>Start Drawing!</button>
                  </Link>
            </section>
            
        </section>
    </div>)
}

export default Dashboard;