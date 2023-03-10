// Require the necessary discord.js classes
const fs = require('node:fs');
const path = require('node:path');
const { Client, Events, GatewayIntentBits, Collection } = require('discord.js');
const  handleEvents  = require('./handlers/eventsHandler');
const  handlePlayer  = require('./handlers/playerEventsHandler');
const  handleInteractions  = require('./handlers/interactionsHandler');
const { Player } = require('discord-player');

// Allows use of dotenv enviroment variables
require('dotenv').config();
const token = process.env.DISCORD_TOKEN;

// Create a new client instance
const client = new Client({ intents: [GatewayIntentBits.Guilds, GatewayIntentBits.GuildVoiceStates, GatewayIntentBits.GuildMessages] });

// Add all avaliable commands to client
// client.commands = new Collection();
// const commandsPath = path.join(__dirname, 'commands');
// const commandFiles = fs.readdirSync(commandsPath).filter(file => file.endsWith('.js'));

// for (const file of commandFiles) {
// 	const filePath = path.join(commandsPath, file);
// 	const command = require(filePath);
// 	// Set a new item in the Collection with the key as the command name and the value as the exported module
// 	if ('data' in command && 'execute' in command) {
// 		client.commands.set(command.data.name, command);
// 	}
// 	else {
// 		console.log(`[WARNING] The command at ${filePath} is missing a required 'data' or 'execute' property.`);
// 	}
// }

const player = new Player(client,
    {
        leaveOnEnd: true,
        leaveOnEmpty: true
    }
);

client.slashCommands = new Collection();
client.contextCommands = new Collection();
client.player = player;
/**
 * Handle events , handle interactions and register commands
 */
handleEvents(client, `${__dirname}/events`);
handlePlayer(client, `${__dirname}/events/player`);
handleInteractions(client, __dirname);

// client.on(Events.InteractionCreate, async interaction => {
// 	if (!interaction.isChatInputCommand()) return;
// 	const command = interaction.client.commands.get(interaction.commandName);

// 	if (interaction.commandName === 'play' | interaction.commandName === 'stop') {
// 		if (!interaction.member.voice.channelId) return await interaction.reply({ content: 'You are not in a voice channel!', ephemeral: true });
// 		if (interaction.guild.members.me.voice.channelId && interaction.member.voice.channelId !== interaction.guild.members.me.voice.channelId) return await interaction.reply({ content: 'You are not in my voice channel!', ephemeral: true });
// 		try {
			
// 		}
// 		catch (error) {
// 			console.error(error);
// 			await interaction.reply({ content: 'There was an error while executing this command!', ephemeral: true });
// 		}
// 	}

// 	if (!command) {
// 		console.error(`No command matching ${interaction.commandName} was found.`);
// 		return;
// 	}

	
// });

// When the client is ready, run this code (only once)
// We use 'c' for the event parameter to keep it separate from the already defined 'client'
client.once(Events.ClientReady, (c) => {
	console.log(`Ready! Logged in as ${c.user.tag}`);
});

// Log in to Discord with your client's token
client.login(token);
