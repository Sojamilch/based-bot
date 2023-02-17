const { SlashCommandBuilder } = require('discord.js');

module.exports = {
	data: new SlashCommandBuilder()
		.setName('stop')
		.setDescription('stops the current song'),
	async execute(interaction,player) {

		const queue = await player.getQueue(interaction.guild)


		// verify vc connection
		try {
			if (!queue.connection) await queue.connect(interaction.member.voice.channel);
			if (!queue || !queue.playing) return void interaction.followUp({ content: "❌ | No music is being played!" });
		}
		catch {
			queue.destroy();
			return await interaction.reply({ content: 'Failed to join VC!', ephemeral: true });
		}

		await interaction.deferReply();

		queue.skip();

		return interaction.followUp({ content: `Stopped Playing` });
	},
};