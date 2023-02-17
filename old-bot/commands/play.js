
const { SlashCommandBuilder, EmbedBuilder : MessageEmbed } = require('discord.js');
const { QueryType } = require('discord-player');


// Plays music according to user query 
// '/play query: '
module.exports = {
	data: new SlashCommandBuilder()
		.setName('play')
		.setDescription('Plays a song with a supplied query or URL')
		.addStringOption(option =>
			option.setName('query')
				.setDescription('Name or Link of song')
				.setRequired(true)),
	async execute(interaction) {

		const query = interaction.options.getString('query');
		const player = interaction.client.player;

		const queue = await player.createQueue(interaction.guild, {
			ytdlOptions: {
				filter: "audioonly",
				highWaterMark: 1 << 30,
				dlChunkSize: 0,
			},
			metadata: {
				channel: interaction.channel,
			},
			leaveOnEnd: false,
		});

		// verify vc connection
		try {
			if (!queue.connection) await queue.connect(interaction.member.voice.channel);
		}
		catch {
			queue.destroy();
			return await interaction.reply({ content: 'Failed to join VC!', ephemeral: true });
		}

		const track = await player.search(query, {
			requestedBy: interaction.user,
			searchEngine: QueryType.AUTO,
		});
		
		if (!track || !track.tracks.length) {
			return await interaction.editReply({
				content: `❌ | No Video/Song/Playlist was found when searching for : ${track}`,
				ephemeral: true,
			});
		}
		const playEmbed = new MessageEmbed()
		.setColor("Random")
		.setTitle(
			`🎶 | New ${track.playlist ? "playlist" : "song"} Added to queue`,
		);

		if (!track.playlist) {
			const tr = track.tracks[0];
			playEmbed.setThumbnail(tr.thumbnail);
			playEmbed.setDescription(`${tr.title}`);
		}

		if (!queue.playing) {
			track.playlist
				? queue.addTracks(track.tracks)
				: queue.addTrack(track.tracks[0]);
			await queue.play();
			return await interaction.editReply({ embeds: [playEmbed] });
		}
		else if (queue.playing) {
			track.playlist
				? queue.addTracks(track.tracks)
				: queue.addTrack(track.tracks[0]);
			return await interaction.editReply({ embeds: [playEmbed] });
		}

		// const track = await player.search(query, {
		// 	requestedBy: interaction.user,
		// }).then(x => x.tracks[0]);
		// if (!track) return await interaction.followUp({ content: `Song: **${query}** not found` });

		// queue.play(track);

		return await interaction.followUp({ content: `Loading song: **${track.title}**` });
	},
};