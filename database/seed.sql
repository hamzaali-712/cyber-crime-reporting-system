-- ============================================================
-- PECA 2016 Laws Seed Data
-- ============================================================

INSERT INTO laws (section_number, title, category, short_description, full_description, punishment, sort_order) VALUES

('Section 3', 'Unauthorized Access to Information System', 'Unauthorized Access', 
'Accessing any information system without authorization or exceeding authorized access.',
'Whoever intentionally gains unauthorized access to any information system or data shall be guilty of an offense. This includes accessing computer systems, networks, or databases without proper authorization or exceeding the scope of authorized access. The offense covers both direct access and access through any technological means.',
'Imprisonment up to 3 months, or fine up to Rs. 50,000, or both. For sensitive systems: up to 6 months, or fine up to Rs. 100,000, or both.',
1),

('Section 4', 'Unauthorized Copying of Data', 'Data Theft',
'Copying or transmitting data from any information system without authorization.',
'Whoever intentionally and without authorization copies or otherwise acquires any data, information, or program from any information system shall be punished. This covers unauthorized downloading, copying, or transmission of data stored in computer systems or transmitted over networks.',
'Imprisonment up to 6 months, or fine up to Rs. 100,000, or both. For sensitive data: up to 3 years, or fine up to Rs. 500,000, or both.',
2),

('Section 5', 'Interference with Information System', 'System Interference',
'Intentionally interfering with the functioning of any information system.',
'Whoever intentionally interferes with or damages the functioning of any information system by inputting, transmitting, damaging, deleting, deteriorating, altering, or suppressing any data or program shall be guilty. This includes DDoS attacks, malware deployment, and any form of system sabotage.',
'Imprisonment up to 2 years, or fine up to Rs. 500,000, or both. For critical infrastructure: up to 3 years, or fine up to Rs. 1,000,000, or both.',
3),

('Section 6', 'Criminal Ill-Intentioned Data Interference', 'Data Interference',
'Damaging, altering, or suppressing data without authorization with criminal intent.',
'Whoever with criminal intent and without authorization damages, deletes, alters, deteriorates, or makes data unintelligible or useless shall be punished. This covers ransomware attacks, data corruption, and intentional data destruction.',
'Imprisonment up to 3 years, or fine up to Rs. 1,000,000, or both.',
4),

('Section 7', 'Electronic Forgery', 'Forgery & Fraud',
'Creating or altering electronic documents with intent to defraud.',
'Whoever with dishonest intention creates, alters, or has in possession any electronic document or record that was forged shall be guilty. This includes forging digital signatures, emails, certificates, and any electronic records to misrepresent identity or deceive.',
'Imprisonment up to 3 years, or fine up to Rs. 250,000, or both.',
5),

('Section 8', 'Electronic Fraud', 'Forgery & Fraud',
'Committing fraud through electronic means or causing damage through interference with information systems.',
'Whoever with dishonest intention causes any damage or harm to any person through any information system by inputting, altering, or deleting data or by interfering with the functioning of an information system, shall be guilty. This covers online banking fraud, e-commerce fraud, and digital payment manipulation.',
'Imprisonment up to 3 years, or fine up to Rs. 250,000, or both. If financial loss exceeds Rs. 1,000,000: up to 5 years, or fine up to Rs. 5,000,000, or both.',
6),

('Section 9', 'Making/Supplying Device for Offenses', 'Cyber Weapons',
'Manufacturing, possessing, or distributing devices, passwords, or access codes for committing cyber offenses.',
'Whoever produces, makes, obtains, imports, exports, supplies, or offers for sale any device including a computer program, electronic module, card, or data designed or adapted primarily for the purpose of committing cyber crimes, or possesses passwords or access codes for criminal purposes shall be punished.',
'Imprisonment up to 6 months, or fine up to Rs. 50,000, or both.',
7),

('Section 10', 'Cyber Terrorism', 'Terrorism',
'Using information systems with intent to create terror, fear, or insecurity in society.',
'Whoever commits or threatens to commit any of the offenses under this Act with the intent to coerce, intimidate, or create a sense of fear, panic, or insecurity in the Government or the public or a section of the public or community or sect or create a sense of fear or insecurity in society shall be guilty of cyber terrorism.',
'Imprisonment up to 14 years, or fine up to Rs. 50,000,000, or both. Death penalty in cases resulting in death of any person.',
8),

('Section 11', 'Hate Speech', 'Content Offenses',
'Preparing or disseminating information through information systems to advance religious, ethnic, or sectarian hatred.',
'Whoever prepares or disseminates information, through any information system or device, that advances or is likely to advance interfaith, sectarian, or racial hatred shall be punished. This covers online content that incites violence, discrimination, or hostility against any group.',
'Imprisonment up to 7 years, or fine up to Rs. 10,000,000, or both.',
9),

('Section 12', 'Offenses Against Modesty & Minor Exploitation', 'Sexual Offenses',
'Transmitting sexually explicit content, including child exploitation material.',
'Whoever intentionally and publicly exhibits or displays or transmits any information which superimposes a photograph of the face of a natural person upon any sexually explicit image or video, or which is obscene, or which involves a minor in sexually explicit conduct shall be punished.',
'For adults: imprisonment up to 5 years, or fine up to Rs. 5,000,000, or both. For minors: up to 7 years, or fine up to Rs. 5,000,000, or both.',
10),

('Section 13', 'Child Pornography', 'Sexual Offenses',
'Producing, distributing, or possessing child sexual abuse material through information systems.',
'Whoever intentionally produces, offers, distributes, procures, or possesses child pornography through any information system or device shall be punished. This includes any visual depiction of sexually explicit conduct involving a minor.',
'Imprisonment up to 7 years, or fine up to Rs. 5,000,000, or both.',
11),

('Section 14', 'Malicious Code', 'Malware',
'Creating, distributing, or deploying viruses, worms, trojans, or other malicious software.',
'Whoever writes, offers, makes available, distributes, or transmits malicious code through an information system or device, with intent to cause harm or damage to any information system, data, or critical infrastructure shall be punished. This includes viruses, ransomware, spyware, keyloggers, and trojans.',
'Imprisonment up to 2 years, or fine up to Rs. 1,000,000, or both. For critical systems: up to 5 years, or fine up to Rs. 5,000,000, or both.',
12),

('Section 15', 'Cyber Stalking', 'Harassment',
'Repeatedly contacting, monitoring, or threatening someone through electronic means.',
'Whoever with intent to coerce, intimidate, or harass any person uses information system, network, internet, website, electronic mail or any other similar means of communication to communicate obscene, vulgar, contemptuous, or indecent information, make any suggestion or proposal of an immoral nature, threaten any illegal or immoral act, take a photograph or video of any person and display or distribute it without consent.',
'Imprisonment up to 3 years, or fine up to Rs. 1,000,000, or both. For repeat offenders: up to 5 years.',
13),

('Section 16', 'Spamming', 'Nuisance',
'Transmitting harmful, fraudulent, or unsolicited bulk communications through information systems.',
'Whoever transmits harmful, fraudulent, misleading, illegal, or unsolicited information to any person without express permission or at a volume that obstructs the information system or network shall be punished.',
'Imprisonment up to 3 months, or fine up to Rs. 50,000, or both.',
14),

('Section 17', 'Spoofing', 'Identity Theft',
'Creating fraudulent websites or sending communications with false source information.',
'Whoever establishes a website, or sends any information with a counterfeit source with intent to be believed to be an authentic source by the user of the information system, designed for the purpose of fraud or to obtain any valuable thing from any person, or to cause injury or harm to any person shall be punished. This covers phishing, website cloning, and email spoofing.',
'Imprisonment up to 3 years, or fine up to Rs. 500,000, or both.',
15),

('Section 18', 'Unauthorized Interception', 'Privacy Violations',
'Illegally intercepting non-public transmissions of data within an information system.',
'Whoever intentionally intercepts by technical means, without right, any non-public transmission of data to, from, or within an information system including electromagnetic emissions from an information system carrying such data shall be punished.',
'Imprisonment up to 2 years, or fine up to Rs. 500,000, or both.',
16),

('Section 24', 'Unauthorized Issuance of SIM Cards', 'Telecom Fraud',
'Issuing, selling, or possessing illegally obtained SIM cards or communication devices.',
'Any person who sells, offers for sale, or issues a subscriber identity module (SIM) card to any person without proper verification of identity and maintaining prescribed records, or possesses or distributes SIM cards obtained through fraud or illegal means shall be punished.',
'Imprisonment up to 3 years, or fine up to Rs. 500,000, or both.',
17);
