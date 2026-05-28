import express from "express";
import cors from "cors";
import fs from "fs";
import { execFile } from "child_process";
import multer from "multer";

const storage = multer.memoryStorage();
const upload = multer({ storage });

const PORT = 5001;

const app = express();
app.use(cors());
app.use(express.json());
app.use(express.urlencoded({extended: true}));
app.use("/games", express.static("games"));

app.post("/generate/:routeName", upload.fields([
    {name: "idle"},
    {name: "attack"},
    {name: "fall"},
    {name: "jump"},
    {name: "run"},
    {name: "enemy"},
    {name: "background"},
    {name: "coin"},
    {name: "terrain"},
    {name: "tree"}
]), (req, res) => {
    const {routeName} = req.params;
    const newRoute = `games/${routeName}`;
    fs.mkdirSync(newRoute);
    fs.cpSync("static_game/Code", `${newRoute}/Code`, {recursive: true});

    // create custom_graphics folder
    for (const f of req.files["idle"]){fs.writeFileSync(`${newRoute}/Code/custom_graphics/player/idle/${f.originalname}`, f.buffer )}
    for (const f of req.files["attack"]){fs.writeFileSync(`${newRoute}/Code/custom_graphics/player/attack/${f.originalname}`, f.buffer )}
    for (const f of req.files["fall"]){fs.writeFileSync(`${newRoute}/Code/custom_graphics/player/fall/${f.originalname}`, f.buffer )}
    for (const f of req.files["jump"]){fs.writeFileSync(`${newRoute}/Code/custom_graphics/player/jump/${f.originalname}`, f.buffer )}
    for (const f of req.files["run"]){fs.writeFileSync(`${newRoute}/Code/custom_graphics/player/run/${f.originalname}`, f.buffer )}
    for (const f of req.files["enemy"]){fs.writeFileSync(`${newRoute}/Code/custom_graphics/enemy/${f.originalname}`, f.buffer )}
    for (const f of req.files["background"]){fs.writeFileSync(`${newRoute}/Code/custom_graphics/background/${f.originalname}`, f.buffer )}
    for (const f of req.files["coin"]){fs.writeFileSync(`${newRoute}/Code/custom_graphics/coin/${f.originalname}`, f.buffer )}
    for (const f of req.files["terrain"]){fs.writeFileSync(`${newRoute}/Code/custom_graphics/terrain/${f.originalname}`, f.buffer )}
    for (const f of req.files["tree"]){fs.writeFileSync(`${newRoute}/Code/custom_graphics/tree/${f.originalname}`, f.buffer )}

    execFile("static_game/.venv/bin/pygbag", ["--build", `${newRoute}/Code`], 
        (err, stdout, stderr) => {
            if (err) return res.status(500).json({success: false, message: "Error during build"});
            return res.json({success: true, url: `http://localhost:5001/games/${routeName}/Code/build/web/index.html`});
        });
})

app.listen(PORT || 5001, () => {
  console.log(`Server running on port ${PORT}`);
});