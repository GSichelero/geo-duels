import React, { useEffect, useRef, useState } from "react";
import { useSelector, useDispatch } from 'react-redux';
import { Navigate } from 'react-router-dom';
import Layout from 'components/Layout';
import ClosingAlert from 'components/Alert';
import { updateRoomValues, createSinglePlayerRoom, joinSinglePlayerRoom } from 'features/user';
import useWebSocket from 'react-use-websocket';
import { Wrapper, Status } from "@googlemaps/react-wrapper";

const render = (status) => {
    switch (status) {
      case Status.LOADING:
        return (
        <div className='spinner-border text-primary' role='status'>
            <span className='visually-hidden text-white'>Loading...</span>
        </div>
        );
      case Status.FAILURE:
        return (
            <div className='spinner-border text-primary' role='status'>
                <span className='visually-hidden text-white'>Error</span>
            </div>
            );
      case Status.SUCCESS:
        return null;
    }
};

const icons = [
    'http://maps.google.com/mapfiles/ms/icons/green-dot.png',
    'http://maps.google.com/mapfiles/ms/icons/red-dot.png',
    'http://maps.google.com/mapfiles/ms/icons/purple-dot.png',
    'http://maps.google.com/mapfiles/ms/icons/blue-dot.png',
    'http://maps.google.com/mapfiles/ms/icons/yellow-dot.png',
    'http://maps.google.com/mapfiles/ms/icons/pink-dot.png',
    'http://maps.google.com/mapfiles/ms/icons/orange-dot.png',
  ]
const random = Math.floor(Math.random() * icons.length);

const iconsBig = [];
const iconsSmall = [];

const colors = ['grn', 'purple', 'blu', 'ylw', 'wht'];
const shapes = ['circle', 'diamond', 'stars', 'square', 'blank'];

for (let j = 0; j < shapes.length; j++) {
    for (let i = 0; i < colors.length; i++) {
        if (colors[i] == 'purple' && shapes[j] == 'blank') {
            iconsBig.push(`http://maps.google.com/mapfiles/kml/paddle/go.png`);
            iconsSmall.push(`http://maps.google.com/mapfiles/kml/paddle/go-lv.png`);
            iconsBig.push(`http://maps.google.com/mapfiles/kml/paddle/stop.png`);
            iconsSmall.push(`http://maps.google.com/mapfiles/kml/paddle/stop-lv.png`);
            iconsBig.push(`http://maps.google.com/mapfiles/kml/paddle/pause.png`);
            iconsSmall.push(`http://maps.google.com/mapfiles/kml/paddle/pause-lv.png`);
        } else {   
            iconsBig.push(`http://maps.google.com/mapfiles/kml/paddle/${colors[i]}-${shapes[j]}.png`);
            iconsSmall.push(`http://maps.google.com/mapfiles/kml/paddle/${colors[i]}-${shapes[j]}-lv.png`);
        }
    }
}

for (let i = 1; i <= 10; i++) {
    iconsBig.push(`http://maps.google.com/mapfiles/kml/paddle/${i}.png`);
    iconsSmall.push(`http://maps.google.com/mapfiles/kml/paddle/${i}-lv.png`);
}

let selectedLocation = { lat: 0, lng: 0 };
let panorama;
let map;
let marker;

function MyMapStreetComponentGuess({
    fenway,
    playerName,
    lat,
    lng,
    movingAllowed,
  }) {
    const refMapGuess = useRef();
    const refPanoGuess = useRef();
  
    useEffect(() => {
        let latLngPosition = { lat: lat, lng: lng };
        map = new window.google.maps.Map(refMapGuess.current, {
            center: fenway,
            zoom: 2,
            panControl: false,
            zoomControl: true,
            fullscreenControl: false,
            streetViewControl: false
        });
  
        map.addListener('click', function(e) {
          updateLocation(e.latLng, playerName);
        });
  
        let panorama = new window.google.maps.StreetViewPanorama(refPanoGuess.current, {
            position: latLngPosition,
            pov: {
                heading: 34,
                pitch: 10,
            },
            linksControl: false,
            panControl: false,
            addressControl: false,
            enableCloseButton: false,
            fullscreenControl: false,
            zoomControl: true,
            showRoadLabels: false,
            clickToGo : movingAllowed,
        });
    });
  
    async function updateLocation(positionClicked, playerName) {
        selectedLocation = positionClicked;
        if (marker) {
        marker.setMap(null);
        marker = null;
      }
      marker = new window.google.maps.Marker({
        position: positionClicked,
        title:"Guess",
        label: {
          text: playerName,
          fontWeight: 'bold'
        },
        icon: {
          url: icons[random],
          labelOrigin: new window.google.maps.Point(8, -5)
        }
      });
      marker.setMap(map);
    }
  
    return (
    <div className="flex flex-col md:flex-row h-[88vh] md:h-[75vh] lg:h-[85vh]">
        <div ref={refMapGuess} id="map-single" className="w-full md:w-2/5 h-[90%] md:h-full lg:h-full"></div>
        <div ref={refPanoGuess} id="pano-single" className="w-full md:w-3/5 h-[90%] md:h-full lg:h-full"></div>
    </div>
    );
}

function MyMapComponentResult({
    fenway,
    roomMatchValues
  }) {
    const refMapResult = useRef();
    let playerName = roomMatchValues.room_members.find((player) => player.user_number == roomMatchValues.player_turn).username;
    let playerTurnRoundPick = roomMatchValues.room_members.find((player) => player.user_number == roomMatchValues.player_turn).rounds.find((round) => round.round_number == roomMatchValues.room_round).picking;
    let lat = playerTurnRoundPick.lat;
    let lng = playerTurnRoundPick.lng;
    let correctPosition = new window.google.maps.LatLng(lat, lng);
    let updated = false;
  
    useEffect(() => {
      if (!updated) {
          map = new window.google.maps.Map(refMapResult.current, {
              center: fenway,
              zoom: 2,
              panControl: false,
              zoomControl: true,
              fullscreenControl: false,
              streetViewControl: false
          });
  
          roomMatchValues.room_members.forEach(function(room_member) {
              if (room_member.username == playerName) {
                  marker = new window.google.maps.Marker({
                      position: correctPosition,
                      title:room_member.username,
                      icon: {
                        url: "http://maps.google.com/mapfiles/kml/pal3/icon31.png",
                        labelOrigin: new window.google.maps.Point(8, -5)
                      }
                    });
                    marker.setMap(map);
              }
              else {
                  let geoPoint = room_member.rounds.find((round) => round.round_number == roomMatchValues.room_round).guessings.find((guessing) => guessing.guess_number == roomMatchValues.player_turn);
                  let lat = geoPoint.guess_geopoint.lat;
                  let lng = geoPoint.guess_geopoint.lng;
                  let latLngPosition = { lat: parseFloat(lat), lng: parseFloat(lng) };
                  let random = Math.floor(Math.random() * icons.length);
                  marker = new window.google.maps.Marker({
                      position: latLngPosition,
                      title:room_member.username,
                      icon: {
                        url: icons[random],
                        labelOrigin: new window.google.maps.Point(8, -5)
                      }
                    });
                    marker.setMap(map);
              }
          });
          updated = true;
      }
    });
  
    return (
      <div id="mapsContainer">
        <div ref={refMapResult} id="mapResult" />
        <table className="min-w-full">
            <thead>
                <tr>
                    <th className='text-white font-bold text-bold text-center py-3'>Player</th>
                    <th className='text-white font-bold text-bold text-center py-3'>Points</th>
                    <th className='text-white font-bold text-bold text-center py-3'>Distance Error</th>
                </tr>
            </thead>
            <tbody>
        {
            roomMatchValues.room_members.map(function(room_member) {
              if (room_member.username != playerName) {
                let geoPoint = room_member.rounds.find((round) => round.round_number == roomMatchValues.room_round).guessings.find((guessing) => guessing.guess_number == roomMatchValues.player_turn);;
                let lat = geoPoint.guess_geopoint.lat;
                let lng = geoPoint.guess_geopoint.lng;
                let latLngPosition = new window.google.maps.LatLng(lat, lng);
                let distanceFromCorrectPlace = window.google.maps.geometry.spherical.computeDistanceBetween(correctPosition, latLngPosition);
                let score = 10000 - ((Math.log(distanceFromCorrectPlace) / Math.log(2)) * 400);
                if (score < 0) {
                    score = 0;
                }
                else if (score > 10000) {
                score = 10000;
                }
                return (
                    <tr className=' focus:outline-white rounded-lg w-full sm:w-auto px-5 py-2.5 text-center transition duration-300 ease-in-out hover:bg-black hover:bg-opacity-60'>
                        <td className='text-white font-bold text-bold text-center py-1'>{room_member.username}</td>
                        <td className='text-white font-bold text-bold text-center py-1'>{(score / 100).toFixed(1)}</td>
                        <td className='text-white font-bold text-bold text-center py-1'>{Math.round(distanceFromCorrectPlace / 1000)}Km ({Math.round(distanceFromCorrectPlace)}m)</td>
                    </tr>
                );
              }
          })}
            </tbody>
        </table>
      </div>
    );
}

function MyMapComponentEndGame({
  fenway,
  roomMatchValues
}) {
    const refMap = useRef();

    useEffect(() => {
        map = new window.google.maps.Map(refMap.current, {
            center: fenway,
            zoom: 2,
            panControl: false,
            zoomControl: true,
            fullscreenControl: false,
            streetViewControl: false
        });

        let icon_index = 0;
        roomMatchValues.room_members.forEach(function(picker_room_member) {
            for( let i=1; i<=roomMatchValues.room_configs.number_of_rounds; i++ ) {
                let geoPoint = picker_room_member.rounds.find((round) => round.round_number == i).picking;
                let lat = geoPoint.lat;
                let lng = geoPoint.lng;
                let latLngPosition = { lat: parseFloat(lat), lng: parseFloat(lng) };
                
                if (picker_room_member.username == 'Computer') {
                    marker = new window.google.maps.Marker({
                        position: latLngPosition,
                        title:picker_room_member.username,
                        icon: {
                        url: iconsBig[icon_index],
                        labelOrigin: new window.google.maps.Point(8, -5),
                        scaledSize: new window.google.maps.Size(40, 40),
                        }
                    });
                    marker.setMap(map);
                }

                roomMatchValues.room_members.forEach(function(guesser_room_member) {
                    if (guesser_room_member.user_number != picker_room_member.user_number) {
                        let geoPoint = guesser_room_member.rounds.find((round) => round.round_number == i).guessings.find((guessing) => guessing.guess_number == picker_room_member.user_number);
                        let lat = geoPoint.guess_geopoint.lat;
                        let lng = geoPoint.guess_geopoint.lng;
                        let latLngPosition = { lat: parseFloat(lat), lng: parseFloat(lng) };
                        
                        if (guesser_room_member.username != 'Computer') {
                            marker = new window.google.maps.Marker({
                                position: latLngPosition,
                                title:guesser_room_member.username,
                                icon: {
                                url: iconsSmall[icon_index],
                                labelOrigin: new window.google.maps.Point(8, -5)
                                }
                            });
                            marker.setMap(map);
                        }
                    }
                });
                icon_index++;
            }
        });
    });

    function playAgain() {
        window.location.href = '/proxy-home';
    }

    let playersAndScores = [];
    roomMatchValues.room_members.map(function(room_member) {
        let playerScore = 0;
        let playerDistance = 0;
        let guessingsCount = 0;
        for( let i=1; i<=roomMatchValues.room_configs.number_of_rounds; i++ ) {
            let round = room_member.rounds.find((round) => round.round_number == i);
            for( let j=1; j<=roomMatchValues.room_configs.max_members; j++ ) {
                if (room_member.user_number != j) {
                    let geoPoint = round.guessings.find((guessing) => guessing.guess_number == j);
                    let lat = geoPoint.guess_geopoint.lat
                    let lng = geoPoint.guess_geopoint.lng
                    let selectedPosition = { lat: parseFloat(lat), lng: parseFloat(lng) };

                    let playerPicker = roomMatchValues.room_members.find((member) => member.user_number == j);
                    let pick = playerPicker.rounds.find((round) => round.round_number == i).picking;
                    let latPick = pick.lat;
                    let lngPick = pick.lng;
                    let pickedPosition = { lat: parseFloat(latPick), lng: parseFloat(lngPick) };

                    let distanceFromCorrectPlace = window.google.maps.geometry.spherical.computeDistanceBetween(pickedPosition, selectedPosition);
                    let score = 10000 - ((Math.log(distanceFromCorrectPlace) / Math.log(2)) * 400);
                    if (score < 0) {
                        score = 0;
                    }
                    else if (score > 10000) {
                        score = 10000;
                    }
                    playerScore += score;
                    playerDistance += distanceFromCorrectPlace;
                    guessingsCount++;
                }

            }
        }
        let meanDistance = playerDistance / guessingsCount;
        let meanScore = playerScore / guessingsCount;
        let userName = room_member.username;
        playersAndScores.push({userName, playerScore, meanScore, playerDistance, meanDistance});
        });

        playersAndScores.sort(function(a, b) {
            return b.playerScore - a.playerScore;
        });
        playersAndScores.forEach((obj, index) => obj.rank = index + 1);

        // remove the computer from the list
        playersAndScores = playersAndScores.filter(function(playerResult) {
            return playerResult.userName != 'Computer';
        });

    return (
        <div id="mapsContainer">
          <table className="min-w-full">
            <thead>
                <tr>
                    <th className='text-white font-bold text-bold text-center py-3'>Player</th>
                    <th className='text-white font-bold text-bold text-center py-3'>Average Score</th>
                    <th className='text-white font-bold text-bold text-center py-3'>Average Distance Error</th>
                    <th className='text-white font-bold text-bold text-center py-3'>Total Score</th>
                    <th className='text-white font-bold text-bold text-center py-3'>Total Distance Error</th>
                </tr>
            </thead>
            <tbody>
          {
            playersAndScores.map(function(playerResult) {
                return (
                    <tr className='focus:outline-white rounded-lg w-full sm:w-auto px-5 py-2.5 text-center transition duration-300 ease-in-out hover:bg-black hover:bg-opacity-60'>
                        <td className='text-white font-bold text-bold text-center py-1'>{playerResult.userName}</td>
                        <td className='text-white font-bold text-bold text-center py-1'>{(playerResult.meanScore / 100).toFixed(1)}%</td>
                        <td className='text-white font-bold text-bold text-center py-1'>{Math.round(playerResult.meanDistance / 1000)}Km ({Math.round(playerResult.meanDistance)}m)</td>
                        <td className='text-white font-bold text-bold text-center py-1'>{(playerResult.playerScore / 100).toFixed(1)}</td>
                        <td className='text-white font-bold text-bold text-center py-1'>{Math.round(playerResult.playerDistance / 1000)}Km ({Math.round(playerResult.playerDistance)}m)</td>
                    </tr>
                );
            })}
                </tbody>
            </table>
            <div ref={refMap} id="mapResult" />
            <button className='mt-2 text-blue-700 text-bold bg-white hover:bg-blue-100 focus:ring-4 focus:outline-none focus:ring-blue-300 font-medium rounded-lg text-sm w-full sm:w-auto px-5 py-2.5 text-center'
                onClick={playAgain}>Play another Game!
            </button>
        </div>
      );
}

function CalculateTimeLeftGuess({remainingTime, userName, roundPlayerName, sendMessage, state}) {
    const [seconds, setSeconds] = useState(Number(remainingTime));
    const [submitPhrase, setSubmitPhrase] = useState("Loading...");
    const [secondPhrase, setSecondPhrase] = useState("Loading...");
    const [remainingTimeOld, setRemainingTimeOld] = useState(remainingTime);
    const [roundPlayerNameOld, setRoundPlayerNameOld] = useState(roundPlayerName);
    const [stateOld, setStateOld] = useState(state);
  
    useEffect(() => {
        if (remainingTimeOld != Number(remainingTime) || roundPlayerNameOld != roundPlayerName || stateOld != state) {
            setSeconds(Number(remainingTime));
            setRemainingTimeOld(Number(remainingTime));
            setRoundPlayerNameOld(roundPlayerName);
            setStateOld(state);
            if (state == "guessing" && roundPlayerName == userName) {
                sendMessage(JSON.stringify({ 'guess': {'lat': 0, 'lng': 0} }));
            }
        }
        if (seconds > 0) {
            const timer = () => setTimeout(() => setSeconds(seconds - 1), 1000);
            const timerId = timer();
            if (state == 'guessing') {
                setSecondPhrase(`Location chosen by: ${roundPlayerName}!`);
                if (userName == roundPlayerName) {
                    setSubmitPhrase('The other players are guessing your location, wait a little!');
                }
                else {
                    setSubmitPhrase('Guess the location!');
                }
            }
            else if (state == 'picking') {
                setSecondPhrase('The other players will have to guess the location you choose!');
                setSubmitPhrase('Pick a location!');
            }
            else if (state == 'results') {
                setSubmitPhrase(' ');
                setSecondPhrase(' ');
            }
            return () => {
                clearTimeout(timerId);
            };
        }

        else if (seconds <= 0) {
            if (state == 'guessing') {
                sendMessage(JSON.stringify({ 'guess': {'lat': 0, 'lng': 0} }));
            }
            else if (state == 'picking') {
                sendMessage(JSON.stringify({ 'pick': {'lat': 0, 'lng': 0} }));
            }
            else if (state == 'results') {
                sendMessage(JSON.stringify({ 'results': {'lat': 0, 'lng': 0} }));
            }
            setSubmitPhrase('Your chosen location was sent!');
        }
    });

    function iAmReady() {
        if (state == 'guessing') {
            sendMessage(JSON.stringify({ 'guess': {'lat': selectedLocation.lat(), 'lng': selectedLocation.lng()} }));
        }
        else if (state == 'picking') {
            sendMessage(JSON.stringify({ 'pick': {'lat': selectedLocation.lat(), 'lng': selectedLocation.lng()} }));
        }
        else if (state == 'results') {
            sendMessage(JSON.stringify({ 'results': {'lat': 0, 'lng': 0} }));
        }
        setSubmitPhrase('Your chosen location was sent!');
    }

    if (state == 'guessing') {
        return (
            <div>
            <h2 className="text-white font-bold">{`Time left: ${seconds} seconds! ${submitPhrase}`}</h2>
            <button className='text-white text-bold bg-green-600 hover:bg-green-400 focus:ring-4 focus:outline-none focus:ring-blue-300 font-medium rounded-lg text-sm w-full sm:w-auto px-5 py-2.5 text-center'
                onClick={iAmReady}>Choose Location!
            </button>
            </div>
        );
    }
    else if (state == 'results') {
        return (
            <div>
            </div>
        );
    }
}

const SinglePlayerMatchPage = () => {
    const dispatch = useDispatch();
	const { isAuthenticated, user, loading, registered, joinedRoom, roomMatchValues, roomMatchCurrentTime } = useSelector(state => state.user);
    let room_name = 'reload';
    let room_owner = 'default';
    let url = process.env.REACT_APP_WS_URL;
    let room_password = 'reload';
    let user_nickname = 'default';
    if (joinedRoom) {
        room_name = joinedRoom.room_name;
        room_owner = joinedRoom.room_owner;
        url = `${process.env.REACT_APP_WS_URL}/ws/spmatch/${room_name}/`;
        room_password = joinedRoom.room_password;
        user_nickname = 'You';
    }

    const center = { lat: 0, lng: 0 };

    const ref = React.useRef(null);
    const [map, setMap] = React.useState();
    React.useEffect(() => {
        if (ref.current && !map) {
          setMap(new window.google.maps.Map(ref.current, {}));
        }
    }, [ref, map]);

    const { lastJsonMessage, sendMessage } = useWebSocket(url, {
    onOpen: () => console.log(`Connected to App WS`),
    onMessage: () => {},
    queryParams: { 'password': room_password, 'username': user_nickname },
    onError: (event) => { console.error(event); return <Navigate to='/login' />; },
    shouldReconnect: (closeEvent) => false,
    reconnectInterval: 3000
    });

    if (lastJsonMessage != null && lastJsonMessage["room"] != roomMatchValues) {
        dispatch(updateRoomValues({ "newRoom": lastJsonMessage["room"], "currentTime": lastJsonMessage["current_time"] }));
    }

    const WrapperMaps = React.useMemo(() => {
        if (!roomMatchValues) {
            dispatch(joinSinglePlayerRoom({ room_name, room_password }));
        }

        else if (roomMatchValues.room_state == 'waiting') {
            return (
                <div>
                    <button className='text-blue-700 text-bold bg-white hover:bg-blue-100 focus:ring-4 focus:outline-none focus:ring-blue-300 font-medium rounded-lg text-sm w-full py-3 px-4 mt-1 mb-4'
                        onClick={() => sendMessage(JSON.stringify({ 'ready': 'yes' }))}>I'm Ready!
                    </button>
                    <div>
                        <ClosingAlert text={'You will have to guess where these 5 places are located based only on the Street View Image!'} color={'blue'} />
                        <ClosingAlert text={'Click on the map where you think the image on the right is located and then click on "Choose Location" button!'} color={'pink'} />
                        <ClosingAlert text={"After you make your guess, you will see a a map with your answer and the correct location and then move to the next round!"} color={'yellow'} />
                    </div>
                </div>
            );
        }

        else if (roomMatchValues.room_state == 'guessing') {
            let remainingTime = Math.ceil(roomMatchValues.room_deadline_time - roomMatchCurrentTime);

            let roundPlayerName;
            for (let i = 0; i < roomMatchValues.room_members.length; i++) {
                if (roomMatchValues.room_members[i].user_number == roomMatchValues.player_turn) {
                    roundPlayerName = roomMatchValues.room_members[i].username;
                }
            }
            
            let playerTurnRoundPick = roomMatchValues.room_members.find((player) => player.user_number == roomMatchValues.player_turn).rounds.find((round) => round.round_number == roomMatchValues.room_round).picking;
            let latPick = playerTurnRoundPick.lat;
            let lngPick = playerTurnRoundPick.lng;

            let movingAllowed = roomMatchValues.room_configs.moving_allowed;

            return (
                <div id="mapsContainer">
                    <Wrapper apiKey={process.env.REACT_APP_MAPS_API_KEY} render={render} libraries={["geometry"]}>
                        <MyMapStreetComponentGuess fenway={center} playerName={user_nickname} lat={latPick} lng={lngPick} movingAllowed={movingAllowed}/>
                        <CalculateTimeLeftGuess remainingTime={remainingTime} userName={user_nickname} roundPlayerName={roundPlayerName} sendMessage={sendMessage} state={roomMatchValues.room_state}/>
                    </Wrapper>
                </div>
            );
        }

        else if (roomMatchValues.room_state == 'results') {
            let remainingTime = Math.ceil(roomMatchValues.room_deadline_time - roomMatchCurrentTime);

            let roundPlayerName;
            for (let i = 0; i < roomMatchValues.room_members.length; i++) {
                if (roomMatchValues.room_members[i].user_number == roomMatchValues.player_turn) {
                    roundPlayerName = roomMatchValues.room_members[i].username;
                }
            }
            
            return (
                <div id="mapsContainer">
                    <Wrapper apiKey={process.env.REACT_APP_MAPS_API_KEY} render={render} libraries={["geometry"]}>
                        <MyMapComponentResult fenway={center} roomMatchValues={roomMatchValues}/>
                        <CalculateTimeLeftGuess remainingTime={remainingTime} userName={user_nickname} roundPlayerName={roundPlayerName} sendMessage={sendMessage} state={roomMatchValues.room_state}/>
                    </Wrapper>
                </div>
            );
        }

        else if (roomMatchValues.room_state == 'endgame') {
            return (
                <div id="mapsContainer">
                    <Wrapper apiKey={process.env.REACT_APP_MAPS_API_KEY} render={render} libraries={["geometry"]}>
                        <MyMapComponentEndGame fenway={center} roomMatchValues={roomMatchValues}/>
                    </Wrapper>
                </div>
            );
        }

        else {
            return (
                <ClosingAlert text={'Click on the Play tab!'} color={'red'} />
            );
        }
    }, [roomMatchValues]);

	return (
		<Layout title='Geo Duels | Home' content='Home page'>
            {WrapperMaps}
		</Layout>
	);
};

export default SinglePlayerMatchPage;