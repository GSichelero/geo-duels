import React from "react";

const Alert = ({ color, text }) => {
  const [showAlert, setShowAlert] = React.useState(true);
  let colorClass = "";
    switch (color) {
        case "green":
            colorClass = "text-white px-6 py-4 border-0 m-5 rounded relative mb-4 bg-green-500";
            break;
        case "red":
            colorClass = "text-white px-6 py-4 border-0 m-5 rounded relative mb-4 bg-red-500";
            break;
        case "yellow":
            colorClass = "text-white px-6 py-4 border-0 m-5 rounded relative mb-4 bg-yellow-500";
            break;
        case "blue":
            colorClass = "text-white px-6 py-4 border-0 m-5 rounded relative mb-4 bg-blue-500";
            break;
        case "pink":
            colorClass = "text-white px-6 py-4 border-0 m-5 rounded relative mb-4 bg-pink-500";
            break;
    }
  return (
    <>
      {showAlert ? (
        <div
          className={colorClass}
        >
          <span className="text-xl inline-block mr-5 align-middle">
            <i className="fas fa-bell" />
          </span>
          <span className="inline-block align-middle mr-8">
            <b className="text-white">{text}</b>
          </span>
          <button
            className="absolute bg-transparent text-2xl font-semibold leading-none right-0 top-0 mt-4 mr-6 outline-none focus:outline-none"
            onClick={() => setShowAlert(false)}
          >
            <span>×</span>
          </button>
        </div>
      ) : null}
    </>
  );
};

export default function ClosingAlert({ text, color }) {
  return (
    <>
      <Alert color={color} text={text} />
    </>
  );
}