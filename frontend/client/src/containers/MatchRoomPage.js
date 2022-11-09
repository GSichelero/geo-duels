import React, { useEffect, useRef, useState } from "react";
import { useSelector, useDispatch } from 'react-redux';
import { Navigate } from 'react-router-dom';
import Layout from 'components/Layout';
import { getFriends, createRoom, updateRoomValues } from 'features/user';
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

function shuffle(obj1, obj2) {
    let index = obj1.length;
    let rnd, tmp1, tmp2;
  
    while (index) {
      rnd = Math.floor(Math.random() * index);
      index -= 1;
      tmp1 = obj1[index];
      tmp2 = obj2[index];
      obj1[index] = obj1[rnd];
      obj2[index] = obj2[rnd];
      obj1[rnd] = tmp1;
      obj2[rnd] = tmp2;
    }
}

function MyMapComponent({center, zoom}) {
    const ref = useRef();
  
    useEffect(() => {
      new window.google.maps.Map(ref.current, {center,zoom});
    });
  
    return <div ref={ref} id="map" />;
}


let selectedLocation = { lat: -31.55542202732198, lng: -54.54408893196694 };
let panorama;
let map;
let marker;

function MyMapStreetComponentPick({
    fenway,
    playerName,
    lat,
    lng,
  }) {
    const refMap = useRef();
    const refPano = useRef();
  
    useEffect(() => {
        map = new window.google.maps.Map(refMap.current, {
            center: fenway,
            zoom: 2,
            panControl: false,
            zoomControl: true,
            fullscreenControl: false,
            // streetViewControl: false
        });
        panorama = new window.google.maps.StreetViewPanorama(refPano.current, {
            position: fenway,
            pov: {
            heading: 34,
            pitch: 10,
            },
            linksControl: false,
            panControl: false,
            addressControl: false,
            enableCloseButton: false,
            zoomControl: true,
            fullscreenControl: false,
        });
        map.setStreetView(panorama);
    }, []);
  
    function updateLocation() {
        selectedLocation = panorama.getPosition();
        if (marker) {
            marker.setMap(null);
            marker = null;
        }
        marker = new window.google.maps.Marker({
            position: selectedLocation,
            title:"Pick",
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
      <div id="mapsContainer">
        <div ref={refMap} id="map" />
        <div ref={refPano} id="pano" />
        <button className='text-blue-700 text-bold bg-white hover:bg-blue-100 focus:ring-4 focus:outline-none focus:ring-blue-300 font-medium rounded-lg text-sm w-full sm:w-auto px-5 py-2.5 text-center dark:bg-blue-600 dark:hover:bg-blue-700 dark:focus:ring-blue-800'
            onClick={updateLocation}>Select Location!
        </button>
      </div>
    );
  }

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
      <div id="mapsContainer">
        <div ref={refMapGuess} id="map" />
        <div ref={refPanoGuess} id="pano" />
      </div>
    );
}

function MyMapComponentEndGame({
  fenway,
  docData
}) {
    const refMap = useRef();
    let map;
    let marker;

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
        let player_number = 1;
        Object.keys(docData['docData']['playersInfo']).sort().forEach(function(player_name) {
            let key = docData['docData']['playersInfo'][player_name];
            for( let i=0; i< Object.keys(key).length; i++ ) {
                let round = key[Object.keys(key).sort()[i]];
                let geoPoint = Object.values(round['picking']);
                let lat = geoPoint[0];
                let lng = geoPoint[1];
                let latLngPosition = { lat: parseFloat(lat), lng: parseFloat(lng) };
                let random = Math.floor(Math.random() * iconsBig.length);

                marker = new window.google.maps.Marker({
                    position: latLngPosition,
                    title:player_name,
                    label: {
                    text: player_name,
                    fontWeight: 'bold'
                    },
                    icon: {
                    url: iconsBig[icon_index],
                    labelOrigin: new window.google.maps.Point(8, -5),
                    scaledSize: new window.google.maps.Size(40, 40),
                    }
                });
                marker.setMap(map);

                
                Object.keys(docData['docData']['playersInfo']).sort().forEach(function(new_player_name) {
                    if (new_player_name != player_name) {
                        let key_new = docData['docData']['playersInfo'][new_player_name];
                        let guesser_round = key_new[Object.keys(key_new).sort()[i]];
                        let geoPoint = Object.values(guesser_round['guessings'][player_number]);
                        let lat = geoPoint[0];
                        let lng = geoPoint[1];
                        let latLngPosition = { lat: parseFloat(lat), lng: parseFloat(lng) };

                        marker = new window.google.maps.Marker({
                            position: latLngPosition,
                            title:new_player_name,
                            label: {
                            text: new_player_name,
                            fontWeight: 'bold'
                            },
                            icon: {
                            url: iconsSmall[icon_index],
                            labelOrigin: new window.google.maps.Point(8, -5)
                            }
                        });
                        marker.setMap(map);
                    }
                });
                icon_index++;
            }
            player_number++;
        });
    });
    let player_number = 1;

    function playAgain() {
        return <Navigate to="/play"/>
    }

    return (
        <div id="mapsContainer">
          <div ref={refMap} id="mapResult" />
          {
            Object.keys(docData['docData']['playersInfo']).sort().map(function(player_name) {
                var playerScore = 0;
                var playerDistance = 0;
                var guessingsCount = 0;
                let key = docData['docData']['playersInfo'][player_name];
                for( let i=0; i<Object.keys(key).length; i++ ) {
                    let round = key[Object.keys(key).sort()[i]];
                    for( let j=0; j<Object.keys(round['guessings']).length; j++ ) {
                        if (key != docData['docData']['playersInfo'][Object.keys(docData['docData']['playersInfo']).sort()[j]]){
                            let geoPoint = Object.values(round['guessings'][`${j + 1}`]);
                            let lat = geoPoint[0];
                            let lng = geoPoint[1];
                            let selectedPosition = { lat: parseFloat(lat), lng: parseFloat(lng) };
    
                            let playerPicker = docData['docData']['playersInfo'][Object.keys(docData['docData']['playersInfo']).sort()[j]];
                            let pick = Object.values(playerPicker[Object.keys(playerPicker).sort()[i]]['picking']);
                            let latPick = pick[0];
                            let lngPick = pick[1];
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
                return (<h2>{player_name}: {Math.round(playerScore)} Points! ------ {Math.round(playerDistance / 1000)}Km of error in total! ------ Average score: {Math.round(meanScore)} ------ Average distance error: {Math.round(meanDistance / 1000)}Km ({Math.round(meanDistance)}m)</h2>)
            })
            }
            <button className="ready" onClick={playAgain}>Play another Game!</button>
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
        }
        if (seconds > 0) {
            const timer = () => setTimeout(() => setSeconds(seconds - 1), 1000);
            const timerId = timer();
            if (state == 'guessing') {
                setSecondPhrase(`Location chosen by: ${roundPlayerName}!`)
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
        setSubmitPhrase('Your chosen location was sent!');
    }

    return (
        <div>
        <h2 className="text-white font-bold">{`Time left: ${seconds} seconds! ${submitPhrase}`}</h2>
        <h2 className="text-white font-bold">{`${secondPhrase}`}</h2>
        <button className='text-blue-700 text-bold bg-white hover:bg-blue-100 focus:ring-4 focus:outline-none focus:ring-blue-300 font-medium rounded-lg text-sm w-full sm:w-auto px-5 py-2.5 text-center dark:bg-blue-600 dark:hover:bg-blue-700 dark:focus:ring-blue-800'
            onClick={iAmReady}>Send Location!
        </button>
        </div>
    );
}

const MatchRoomPage = () => {
    const dispatch = useDispatch();
	const { isAuthenticated, user, loading, registered, joinedRoom, roomMatchValues } = useSelector(state => state.user);
    let room_name = 'reload';
    let room_owner = 'reload';
    let url = 'ws://127.0.0.1:8000/';
    let room_password = 'reload';
    let user_nickname = 'reload';
    if (joinedRoom) {
        room_name = joinedRoom.room_name;
        room_owner = joinedRoom.room_owner;
        url = `ws://127.0.0.1:8000/ws/room/${room_name}/`;
        room_password = joinedRoom.room_password;
        user_nickname = user.nickname;
    }

    const center = { lat: -34.397, lng: 150.644 };
    const zoom = 4;

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
        dispatch(updateRoomValues({ "newRoom": lastJsonMessage["room"] }));
    }

    const WrapperMaps = React.useMemo(() => {
        if (!roomMatchValues) {
            return (
                <h2 className="text-white font-bold">Click on the Play tab</h2>
            );
        }

        else if (roomMatchValues.room_state == 'waiting') {
            console.log(roomMatchValues);
            let playersConnected = roomMatchValues.room_members.map((player) => player.username);
            let playersReady = roomMatchValues.room_members.filter((player) => player.is_ready).map((player) => player.username);
            return (
                <div>
                    <h1 className="text-3xl font-bold text-white text-center m-12">Room Name: {room_name}</h1>
                    <h1 className="text-3xl font-bold text-white text-center m-12">Room Owner: {room_owner}</h1>
                    <h2 className="text-white font-bold">Waiting for players to join the room...</h2>
                    <h2 className="text-white font-bold">Players connected: {playersConnected.join(', ')}</h2>
                    <h2 className="text-white font-bold">Players ready: {playersReady.join(', ')}</h2>
                    <button className='text-blue-700 text-bold bg-white hover:bg-blue-100 focus:ring-4 focus:outline-none focus:ring-blue-300 font-medium rounded-lg text-sm w-full sm:w-auto px-5 py-2.5 text-center dark:bg-blue-600 dark:hover:bg-blue-700 dark:focus:ring-blue-800'
                        onClick={() => sendMessage(JSON.stringify({ 'ready': 'yes' }))}>I'm Ready!
                    </button>
                </div>
            );
        }

        else if (roomMatchValues.room_state == 'picking') {
            let now = new Date();
            let utc_timestamp = now.getTime() + (now.getTimezoneOffset() * 60000);
            let seconds = (utc_timestamp) / 1000;
            let remainingTime = Math.floor(roomMatchValues.room_deadline_time - seconds);
            return (
                <div id="mapsContainer">
                    <Wrapper apiKey={process.env.MAPS_API_KEY} render={render} libraries={["geometry"]}>
                        <MyMapStreetComponentPick fenway={center} playerName={user.nickname} lat={-34.397} lng={150.644}/>
                        <CalculateTimeLeftGuess remainingTime={remainingTime} userName={user.nickname} roundPlayerName={'picking phase'} sendMessage={sendMessage} state={roomMatchValues.room_state}/>
                    </Wrapper>
                </div>
            );
        }

        else if (roomMatchValues.room_state == 'guessing') {
            let now = new Date();
            let utc_timestamp = now.getTime() + (now.getTimezoneOffset() * 60000);
            let seconds = (utc_timestamp) / 1000;
            let remainingTime = Math.floor(roomMatchValues.room_deadline_time - seconds);

            let roundPlayerName;
            for (let i = 0; i < roomMatchValues.room_members.length; i++) {
                if (roomMatchValues.room_members[i].user_number == roomMatchValues.player_turn) {
                    roundPlayerName = roomMatchValues.room_members[i].user_nickname;
                }
            }
            
            let playerTurnRoundPick = roomMatchValues.room_members.find((player) => player.user_number == roomMatchValues.player_turn).rounds.find((round) => round.round_number == roomMatchValues.room_round).picking;
            let latPick = playerTurnRoundPick.lat;
            let lngPick = playerTurnRoundPick.lng;

            let movingAllowed = roomMatchValues.room_configs.moving_allowed;

            return (
                <div id="mapsContainer">
                    <Wrapper apiKey={process.env.MAPS_API_KEY} render={render} libraries={["geometry"]}>
                        <MyMapStreetComponentGuess fenway={center} playerName={user.nickname} lat={latPick} lng={lngPick} movingAllowed={movingAllowed}/>
                        <CalculateTimeLeftGuess remainingTime={remainingTime} userName={user.nickname} roundPlayerName={roundPlayerName} sendMessage={sendMessage} state={roomMatchValues.room_state}/>
                    </Wrapper>
                </div>
            );
        }

        else if (roomMatchValues.room_state == 'results') {
            return (
                <div id="mapsContainer">
                    <Wrapper apiKey={process.env.MAPS_API_KEY} render={render} libraries={["geometry"]}>
                        <MyMapComponentEndGame fenway={center}/>
                    </Wrapper>
                </div>
            );
        }

        else {
            return (
                <h2 className="text-white font-bold">Click on the Play tab</h2>
            );
        }
    }, [roomMatchValues]);

	return (
		<Layout title='Geo Duels | Home' content='Home page'>
            {WrapperMaps}
		</Layout>
	);
};

export default MatchRoomPage;