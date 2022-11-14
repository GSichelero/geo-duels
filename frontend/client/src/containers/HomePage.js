import Layout from 'components/Layout';

const HomePage = () => {
	return (
		<Layout title='Geo Duels | Home' content='Home page'>
			<h1 className="text-7xl font-bold text-white text-center m-12">Geo Duels</h1>
			<img className="w-2/5 mx-auto filter-white" src="globe-icon.svg" alt="Geo Duels Logo" />
		</Layout>
	);
};

export default HomePage;
