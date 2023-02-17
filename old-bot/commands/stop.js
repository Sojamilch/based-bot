const { SlashCommandBuilder } = require('discord.js');

// Stops and destroys current music queue
// '/stop'
module.exports = {
	data: new SlashCommandBuilder()
		.setName('stop')
		.setDescription('stops the current song'),
	async execute(interaction) {

		const player = interaction.client.player;
		const queue = player.getQueue(interaction.guild);	
		// const db = interaction.client.db;
		// const guild = interaction.guildId;

		if (!queue || !queue.playing) 
			return void interaction.editReply({ content: "❌ | No music is being played!" });

		queue.destroy();

		return interaction.editReply({ content: `Stopped Playing` });
	},
};