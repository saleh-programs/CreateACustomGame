import { useEffect, useRef, useState } from "react";
import { Canvas, PencilBrush, Rect, Circle, Line, Textbox } from "fabric";

import circleIcon from "../assets/circle.png"
import rectangleIcon from "../assets/rectangle.png"
import lineIcon from "../assets/line.png"
import pencilIcon from "../assets/pencil.png"
import eraserIcon from "../assets/eraser.png"
import colorMatcherIcon from "../assets/colorMatcher.png"
import textIcon from "../assets/text.png"
import timerIcon from "../assets/stopwatch.png"

import bg from "../assets/background.jpg"


const toolBtn = {
  width: 42,
  height: 42,
  borderRadius: "12px",
  border: "1px solid rgba(255,255,255,0.3)",
  background: "rgba(255,255,255,0.9)",
  cursor: "pointer",
  fontSize: "18px",
  boxShadow: "0 6px 14px rgba(0,0,0,0.18)",
  display: "flex",
  justifyContent: "center",
  alignItems: "center"
};

function Creating() {
  const [allAssets, setAllAssets] = useState([
    { title: "...the main character standing!",
      dimensions: [40,64],
      name: "idle",
      countdown: 10000
      },
    { title: "...the main character attacking!",
      dimensions: [240, 74],
      name: "attack",
      countdown: 10000
      },
    { title: "...the main character falling!" ,
      dimensions: [44,64],
      name: "fall",
      countdown: 10000
    },
    { title: "...the main character jumping!",
      dimensions: [44,64],
      name: "jump",
      countdown: 10000
      },
    { title: "...the main character running! (frame 1 of 3)",
      dimensions: [40,64],
      name: "run",
      countdown: 10000
      },
    { title: "...the main character running! (frame 2 of 3)",
      dimensions: [40,64],
      name: "run",
      countdown: 10000
      },
    { title: "...the main character running! (frame 3 of 3)",
      dimensions: [40,64],
      name: "run",
      countdown: 10000
      },
    { title: "...an enemy! (frame 1 of 2)",
      dimensions: [64,64],
      name: "enemy",
      countdown: 10000
      },
    { title: "...an enemy! (frame 2 of 2)",
      dimensions: [64,64],
      name: "enemy",
      countdown: 10000
      },
    { title: "...a background!",
      dimensions: [3600,1900],
      name: "background",
      countdown: 10000
      },
    { title: "...a coin!" ,
      dimensions: [64,64],
      name: "coin",
      countdown: 10000
    },
    { title: "...a terrain block!",
      dimensions: [64,64],
      name: "terrain",
      countdown: 10000
      },
    { title: "...a obstacle, like a tree or bush!",
      dimensions: [64,64],
      name: "tree",
      countdown: 10000
      },
  ]);
  const [currentAsset, setCurrentAsset] = useState(0);
  const currentAssetRef = useRef(0);

  const storedAssets = useRef({
    idle: [],
    attack: [],
    fall: [],
    jump: [],
    run: [],
    enemy: [],
    background: [],
    coin: [],
    terrain: [],
    tree: [],
  });


  const canvasEl = useRef(null);
  const fabricCanvas = useRef(null);

  const [color, setColor] = useState("#000000");
  const [strokeSize, setStrokeSize] = useState(2);
    // const undoStack = useRef([]);
    // const redoStack = useRef([]);
    const isLoadingState = useRef(false);
    const [activeTool, setActiveTool] = useState("pencil");
    const [stopwatch, setStopwatch] = useState(allAssets[currentAsset].countdown);
  const storeIntervalRef = useRef(null);
  const displayScale = getDisplayScale(allAssets[currentAsset].dimensions[0], allAssets[currentAsset].dimensions[1]);
  const [ready, setReady] = useState(false);
  const [generatingGame, setGeneratingGame] = useState(false);
const [loader,setLoader] = useState(".");
const [gaveName, setGaveName] = useState(false);
const [studentName, setStudentName] = useState("");
 
  useEffect(() => {
    if (!ready) return;
    storeIntervalRef.current = setInterval(() => {
      setStopwatch(prev => {
        if (prev - 1000 <= 0){
          const currentName = allAssets[currentAssetRef.current].name;
          getCanvasSnapshot().then((b) => {
            storedAssets.current[currentName].push(b);
          })
          
          if (currentAssetRef.current >= allAssets.length - 1){
            clearInterval(storeIntervalRef.current);
            setGeneratingGame(true);
            return 0;
          }else{
            setCurrentAsset(prev => prev + 1);
            return allAssets[currentAssetRef.current + 1].countdown;
          }
        }
        return prev - 1000;
      });
    },1000);
    return () => {
      clearInterval(storeIntervalRef.current);
    }
  }, [ready])


  useEffect(() => {
    const canvas = new Canvas(canvasEl.current, {
      width: allAssets[currentAsset].dimensions[0],
      height: allAssets[currentAsset].dimensions[1],
      backgroundColor: "transparent",
    });
    currentAssetRef.current = currentAsset;

    fabricCanvas.current = canvas;

    canvas.setDimensions(
      {
        width: allAssets[currentAsset].dimensions[0] * displayScale,
        height: allAssets[currentAsset].dimensions[1] * displayScale,
      },
      {
        cssOnly: true,
      }
    );

    usePencil();

    return () => canvas.dispose();
  }, [currentAsset]);

useEffect(() => {
  if (!generatingGame) return;

  const t = setInterval(() => {
    setLoader(prev => (prev + 1) % 5);
  }, 200);

  return () => clearInterval(t);
}, [generatingGame]);
  function getStopwatchTime(){
    const seconds = Math.floor(stopwatch / 1000);
    return `${Math.floor(seconds / 60)}:${String(seconds % 60).padStart(2, "0")}`
  }

  function finishEarly(){
    if (stopwatch < 2000) return;

    const currentName = allAssets[currentAssetRef.current].name;
    getCanvasSnapshot().then((b) => {
      storedAssets.current[currentName].push(b);
    })
    
    if (currentAssetRef.current >= allAssets.length - 1){
      clearInterval(storeIntervalRef.current);
      setStopwatch(0);
      setGeneratingGame(true);
    }else{
      setCurrentAsset(prev => prev + 1);
      setStopwatch(allAssets[currentAssetRef.current + 1].countdown);
    }
  }

  function clearCanvas() {
    const canvas = fabricCanvas.current;
    if (!canvas) return;

    canvas.clear();
    canvas.backgroundColor = "transparent";
    canvas.renderAll();
  }

function usePencil() {
  const canvas = fabricCanvas.current;
  if (!canvas) return;

  canvas.off("mouse:move");

  canvas.isDrawingMode = true;
  canvas.selection = true;
canvas.skipTargetFind = false;


  const brush = new PencilBrush(canvas);
  brush.color = color;
  brush.width = strokeSize;

  canvas.freeDrawingBrush = brush;
  canvas.contextTop.globalCompositeOperation = "source-over";

}
function useEraser() {
  const canvas = fabricCanvas.current;
  if (!canvas) return;

  canvas.off("mouse:move");

  canvas.isDrawingMode = true;
  canvas.selection = false;

  const brush = new PencilBrush(canvas);
  brush.width = strokeSize;
  brush.color = "#000000";

  const originalFinalize = brush._finalizeAndAddPath.bind(brush);

  brush._finalizeAndAddPath = function () {
    canvas.contextTop.globalCompositeOperation = "destination-out";

    originalFinalize();

    const path = canvas.getObjects().at(-1);
    if (path) {
      path.globalCompositeOperation = "destination-out";
    }

    canvas.contextTop.globalCompositeOperation = "source-over";
    canvas.renderAll();
  };

  canvas.freeDrawingBrush = brush;
}
function useColorMatcher() {
  const canvas = fabricCanvas.current;
  if (!canvas) return;

  canvas.off("mouse:move");
  canvas.off("mouse:down");

  canvas.isDrawingMode = false;
  canvas.selection = false;
  canvas.skipTargetFind = true;

  const pickColor = (opt) => {
    const point = canvas.getScenePoint(opt.e);
    const ctx = canvas.lowerCanvasEl.getContext("2d");

    const pixel = ctx.getImageData(
      Math.floor(point.x),
      Math.floor(point.y),
      1,
      1
    ).data;

    const pickedColor =
      "#" +
      [pixel[0], pixel[1], pixel[2]]
        .map((v) => v.toString(16).padStart(2, "0"))
        .join("");

    setColor(pickedColor);

    canvas.off("mouse:down", pickColor);
    canvas.skipTargetFind = false;
  };

  canvas.on("mouse:down", pickColor);
}
function useCircle() {
  const canvas = fabricCanvas.current;
  if (!canvas) return;

  canvas.isDrawingMode = false;
  canvas.selection = true;

  const circle = new Circle({
    left: 150,
    top: 150,
    radius: 50,
    fill: "transparent",
    stroke: color,
    strokeWidth: strokeSize,
  });

  canvas.add(circle);
  canvas.setActiveObject(circle);
  canvas.renderAll();
}
function useText() {
  const canvas = fabricCanvas.current;
  if (!canvas) return;

  canvas.isDrawingMode = false;
  canvas.selection = true;

  const text = new Textbox("Text", {
    left: 100,
    top: 100,
    width: 200,
    fontSize: 32,
    fill: color,
  });

  canvas.add(text);
  canvas.setActiveObject(text);
  canvas.renderAll();
}
function useLine() {
  const canvas = fabricCanvas.current;
  if (!canvas) return;

  canvas.isDrawingMode = false;
  canvas.selection = true;

  const line = new Line([100, 100, 250, 100], {
    stroke: color,
    strokeWidth: strokeSize,
  });

  canvas.add(line);
  canvas.setActiveObject(line);
  canvas.renderAll();
}
function useRectangle() {
  const canvas = fabricCanvas.current;
  if (!canvas) return;

  canvas.isDrawingMode = false;
  canvas.selection = true;

  const rect = new Rect({
    left: 150,
    top: 150,
    width: 120,
    height: 80,
    fill: "transparent",
    stroke: color,
    strokeWidth: strokeSize,
  });

  canvas.add(rect);
  canvas.setActiveObject(rect);
  canvas.renderAll();
}

async function getCanvasSnapshot(){
  const canvas = fabricCanvas.current;
  if (!canvas) return null;

  return await new Promise((resolve) => {
    canvas.getElement().toBlob(resolve, "image/png");
  })
}

function getDisplayScale(assetW, assetH) {
  const TARGET_VISIBLE_H = 300;

  let scale = TARGET_VISIBLE_H / assetH;

  // Small assets: use whole-number scaling to reduce blur
  if (scale > 1) {
    return Math.floor(scale);
  }

  // Large assets: allow shrinking
  return scale;
}

// function saveState() {
//   const canvas = fabricCanvas.current;
//   if (!canvas || isLoadingState.current) return;

//   const state = getCanvasState();
//   if (!state) return;

//   // undoStack.current.push(state);

//   if (undoStack.current.length > 6) {
//     undoStack.current.shift();
//   }

//   redoStack.current = [];
// }

// function undo() {
//   const canvas = fabricCanvas.current;
//   if (!canvas || undoStack.current.length <= 1) return;

//   const currentState = undoStack.current.pop();
//   redoStack.current.push(currentState);

//   const previousState = undoStack.current[undoStack.current.length - 1];

//   isLoadingState.current = true;
//   canvas.loadFromJSON(previousState).then(() => {
//     canvas.renderAll();
//     isLoadingState.current = false;
//   });
// }

// function redo() {
//   const canvas = fabricCanvas.current;
//   if (!canvas || redoStack.current.length === 0) return;

//   const nextState = redoStack.current.pop();
//   undoStack.current.push(nextState);

//   isLoadingState.current = true;
//   canvas.loadFromJSON(nextState).then(() => {
//     canvas.renderAll();
//     isLoadingState.current = false;
//   });
// }


  if (generatingGame){
    return (
    <div style={{ height: "100%", padding: "20px", backgroundColor: "rgba(109, 31, 0, 0.36)", display: "flex", 
      flexDirection: "column", gap: "10px", justifyContent: "center", alignItems: "center"
    }}>
        <section style={{
          backgroundColor: "white",
          borderRadius: "5px",
          padding: "20px 10px",
          fontSize: "2rem",
          minHeight: "170px"
        }}>
          <div style={{textAlign: "center", fontSize: ".8em", opacity: ".5"}}>{studentName},</div>
          we are generating your game!<br/>
          <div style={{fontSize: "4rem", textAlign: "center"}}>{"".padStart(loader, ".")}</div>
        </section>
    </div>
    )
  }

  return (
    <div style={{ height: "100%", padding: "20px", backgroundColor: "rgba(109, 31, 0, 0.36)", display: "flex", 
      flexDirection: "column", gap: "10px"
    }}>

        {}
        {ready && <section style={{
          fontSize: "1.3em", 
          backgroundColor: "rgb(39, 39, 39)",
          borderRadius: "20px",
          padding: "10px",
          color: "white"}}>
            <h1>You're drawing...</h1>
            <h2 style={{fontStyle: "italic", marginLeft: "30px"}}>{allAssets?.[currentAsset]?.title}</h2>
        </section>}
        { ready 
        ?
          <section
          style={{
              width: "100%",
              minHeight: "500px",
              display: "flex",
              justifyContent: "center",
              alignItems: "center",
              border: "1px solid #2f2f2f",
              background: "linear-gradient(135deg, #4b5563, #1f2937)",
              position: "relative",
              borderRadius: "18px",
          }}
          >
              <section style={{
                backgroundColor: "white", 
                width: ` ${allAssets[currentAsset].dimensions[0] * displayScale}px`,
                height: ` ${allAssets[currentAsset].dimensions[1] * displayScale}px`

                }}>
                  <canvas
                      ref={canvasEl}
                      style={{
                      imageRendering: "pixelated",
                      border: "1px solid #111",
                      width: "100%",
                      height: "100%"
                      }}
                  />
              </section>
              <div style={{ position: "absolute", left: "0", top: "-40px", transform: "scale(.75)", transformOrigin: "top left"}}>
                <img src={timerIcon} alt="" />
                <section style={{
                  position: "absolute",
                  top: "150px",
                  left: "150px",
                  transform: "translate(-50%,-50%)",
                  fontSize: "6rem",
                  fontWeight: "bold",
                  color: stopwatch <= 10000 ? "red" : "white"
                }}>
                  {getStopwatchTime()}
                </section>
              </div>
              <div style={{ position: "absolute", right: "0", bottom: "0"}}>
                <button style={{
                  padding: "10px 25px",
                  fontSize: "3rem",
                  backgroundColor: "green",
                  color: "white",
                  borderRadius: "15px",
                  opacity: stopwatch <= 2000 ? ".3" : "1",
                }}
              onMouseEnter={(e)=>{
                e.target.style.backgroundColor = "white";
                e.target.style.color = "green";
              }}
              onMouseLeave={(e)=>{
                e.target.style.backgroundColor = "green";
                e.target.style.color = "white";
              }}
              disabled={stopwatch <= 2000}
              onClick={finishEarly}>
                  Next
                </button>
              </div>

              {/* top right */}
              <div style={{ position: "absolute", right: "24px", top: "24px" }}>
                  <button style={{...toolBtn, width: "50px", height: "4Opx", padding: "10px 30px"}} onClick={clearCanvas}>Clear</button>            </div>
              <div
              style={{
                  position: "absolute",
                  left: "24px",
                  bottom: "24px",
                  display: "flex",
                  alignItems: "center",
                  gap: "12px",
                  padding: "12px",
                  borderRadius: "16px",
                  background: "rgba(255,255,255,0.14)",
                  backdropFilter: "blur(14px)",
                  border: "1px solid rgba(255,255,255,0.25)",
                  boxShadow: "0 20px 40px rgba(0,0,0,0.25)",
              }}
              >
          <input
          type="color"
          value={color}
          onChange={(e) => {
              setColor(e.target.value);

              const canvas = fabricCanvas.current;
              if (!canvas) return;

              if (canvas.freeDrawingBrush) {
              canvas.freeDrawingBrush.color = e.target.value;
              }

              const active = canvas.getActiveObject();
              if (active) {
              active.set("fill", e.target.value);
              canvas.renderAll();
              }
          }}
          />

              <label style={{ color: "white", fontWeight: 600 }}>
                  Size
              </label>

                  <input
                  type="range"
                  min="1"
                  max="30"
                  value={strokeSize}
                  onChange={(e) => {
                      const size = Number(e.target.value);
                      setStrokeSize(size);

                      const canvas = fabricCanvas.current;
                      if (canvas?.freeDrawingBrush) {
                      canvas.freeDrawingBrush.width = size;
                      }
                  }}
                  />
              </div>

  <aside
    style={{
      position: "absolute",
      left: "24px",
      top: "50%",
      transform: "translateY(-50%)",
      display: "grid",
      gridTemplateColumns: "repeat(4, 1fr)",
      gap: "7px",
      padding: "12px",
      borderRadius: "16px",
      background: "rgba(255,255,255,0.14)",
      backdropFilter: "blur(14px)",
      border: "1px solid rgba(255,255,255,0.25)",
      boxShadow: "0 20px 40px rgba(0,0,0,0.25)",
    }}
  >
    {[
      "#000000", "#ffffff", "#808080", "#c0c0c0",
      "#ff0000", "#ff7f00", "#ffff00", "#00ff00",
      "#00ffff", "#0000ff", "#8b00ff", "#ff00ff",
      "#964b00", "#ffc0cb", "#800000", "#008080",
      "#2f4f4f", "#ffd700", "#90ee90", "#add8e6",
    ].map((c) => (
      <button
        key={c}
        onClick={() => {
          setColor(c);

          const canvas = fabricCanvas.current;
          if (canvas?.freeDrawingBrush) {
            canvas.freeDrawingBrush.color = c;
          }

          const active = canvas?.getActiveObject();
          if (active) {
            active.set("fill", c);
            canvas.renderAll();
          }
        }}
        style={{
          width: "22px",
          height: "22px",
          borderRadius: "6px",
          border: color === c ? "2px solid white" : "1px solid rgba(255,255,255,0.4)",
          background: c,
          cursor: "pointer",
          boxShadow: "0 4px 8px rgba(0,0,0,0.2)",
        }}
      />
    ))}
  </aside>
  <aside
    style={{
      position: "absolute",
      right: "24px",
      top: "50%",
      transform: "translateY(-50%)",
      display: "flex",
      flexDirection: "column",
      gap: "14px",
      padding: "14px",
      borderRadius: "16px",
      background: "rgba(255,255,255,0.14)",
      backdropFilter: "blur(14px)",
      border: "1px solid rgba(255,255,255,0.25)",
      boxShadow: "0 20px 40px rgba(0,0,0,0.25)",
    }}
  >
    <section
      style={{
        display: "grid",
        gridTemplateColumns: "1fr 1fr",
        gap: "8px",
        alignItems: "center"
      }}
    >
      <p style={{ gridColumn: "1 / -1", margin: "auto", color: "white", fontWeight: 700 }}>
        Main
      </p>

      <button style={toolBtn} onClick={usePencil}><img src={pencilIcon} alt="" /></button>
      <button style={toolBtn} onClick={useEraser}><img src={eraserIcon} alt="" /></button>
      <button style={toolBtn} onClick={useColorMatcher}><img src={colorMatcherIcon} alt="" /></button>
      <button style={toolBtn} onClick={useText}><img src={textIcon} alt="" /></button>
    </section>

    <section
      style={{
        display: "grid",
        gridTemplateColumns: "1fr 1fr",
        gap: "8px",
      }}
    >
      <p style={{ gridColumn: "1 / -1", margin: "auto", color: "white", fontWeight: 700 }}>
        Shapes
      </p>

      <button style={toolBtn} onClick={useRectangle}><img src={rectangleIcon} alt="" /></button>
      <button style={toolBtn} onClick={useCircle}><img src={circleIcon} alt="" /></button>
      <button style={{...toolBtn, gridColumn: "1 / -1", justifySelf: "center"}} onClick={useLine}><img src={lineIcon}/></button>
    </section>
  </aside>
          </section>
        : gaveName ? 
        (
          <section
          style={{
              width: "100%",
              minHeight: "500px",
              display: "flex",
              justifyContent: "center",
              alignItems: "center",
              border: "1px solid #2f2f2f",
              background: "linear-gradient(135deg, #4b5563, #1f2937)",
              position: "relative",
              borderRadius: "18px",
              display: "flex",
              flexDirection: "column",
              gap: "20px",
              fontSize: "2.5rem",
              textAlign: "center",
              color: "white"
          }}
          >
            <section>
              Begin when you're ready, you have to complete each image within a certain amount of time!
            </section>
            <button style={{
              padding: "15px",
              fontSize: "2rem",
              borderRadius: "15px",
              backgroundColor: "green",
              color: "white"
            }}
            onClick={() => setReady(true)}
            onMouseEnter={(e)=>{
              e.target.style.backgroundColor = "white";
              e.target.style.color = "green";
            }}
            onMouseLeave={(e)=>{
              e.target.style.backgroundColor = "green";
              e.target.style.color = "white";
            }}
            >START</button>
          </section>
        ) 
        :
          (<section
          style={{
              width: "100%",
              minHeight: "500px",
              display: "flex",
              justifyContent: "center",
              alignItems: "center",
              border: "1px solid #2f2f2f",
              background: "linear-gradient(135deg, #4b5563, #1f2937)",
              position: "relative",
              borderRadius: "18px",
              display: "flex",
              flexDirection: "column",
              gap: "20px",
              fontSize: "2.5rem",
              textAlign: "center",
              color: "white"
          }}
          >
            What is your first and last name?
            <section style={{
              display: "flex"
            }}>
              <input 
              value={studentName}
              onChange={e => setStudentName(e.target.value)}
              type="text" style={{
                padding: '10px',
                fontSize: "2rem"
              }}/>
              <button onClick={() => {
                if (studentName === "") return;
                setGaveName(true);
              }}>Submit</button>
            </section>
          </section>)

        }

        <section style={{
          fontSize: "1.3em", 
          backgroundColor: "rgb(110, 110, 117)",
          borderRadius: "20px",
          padding: "10px",
          color: "white"}}>
            <h1>Important notes:</h1>
            <ul>
              <li>If a character must face a side, face it <strong style={{fontSize: "1.2em"}}>right</strong>!</li>
              <li>Try not to leave too much empty space!</li>
              <li>Try to leave everything in the center!</li>
              <br />
              These ensure your game comes out great!
            </ul>
        </section>
    </div>
  );
}

export default Creating;