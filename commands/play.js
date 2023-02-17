
const { SlashCommandBuilder } = require('discord.js');


module.exports = {
	data: new SlashCommandBuilder()
		.setName('play')
		.setDescription('Plays a song with a supplied query or URL')
		.addStringOption(option =>
			option.setName('query')
				.setDescription('Name or Link of song')
				.setRequired(true)),
	async execute(interaction,player) {


		const query = interaction.options.getString('query');
		const queue = await player.createQueue(interaction.guild, {
			metadata: {
				channel: interaction.channel,
			},
		});

		// verify vc connection
		try {
			if (!queue.connection) await queue.connect(interaction.member.voice.channel);
		}
		catch {
			queue.destroy();
			return await interaction.reply({ content: 'Failed to join VC!', ephemeral: true });
		}

		await interaction.deferReply();
		const track = await player.search(query, {
			requestedBy: interaction.user,
		}).then(x => x.tracks[0]);
		if (!track) return await interaction.followUp({ content: `Song: **${query}** not found` });

		queue.play(track);

		return await interaction.followUp({ content: `Loading song: **${track.title}**` });
	},
};