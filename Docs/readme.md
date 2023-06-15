<l>Background and Rationale:</l>
<p>Waste processing by Black Soldier Fly (BSF) larvae is seen as a promising organic waste treatment
technology, due to the high waste reduction potential while producing valuable products. Young BSF
larvae are placed on organic waste where they feed for about two weeks, reducing the biomass by up
to 70%. The grown larvae will be harvested and sold as a component of animal feed for fish and poultry
or pet food.</p>
<p>For waste treatment, trays are filled with substrate and stocked with a clearly defined number of
young larvae. The production of stocking larvae in constant quality and quantity is therefore a crucial
point in every BSF facility. For the production of young larvae, a nursery is operated with nets in which
the flies mate and lay eggs. These nets, the so-called love cages, are temporarily connected to other
nets (dark cages) from where flies fly into the love cages. The number of these flies should be counted
with a sensor.</p>
<l>Raspberry Pi:</l>
<p>The controller used is the Raspberry Pi 4 
model B with 8GB RAM. The Raspberry Pi is
used with its official touchscreen with case
where the GUI (graphical user interface) is
visualized and with the official PiCamera
that is used to scan the cages’ QR codes.</p>
<l>Sensor:</l>
<p>The sensor is a light grid LF 48/5 270 T/S with 48 infrared light beams, each 5mm apart (see “Manual 
light grid”). It consists of two separate elements: the transmitter (TX) and the receiver (RX). They are
both connected to a control unit (FAW). Its output for the communication with the Raspberry Pi is a
serial interface. The status of every beam can be transmitted (see “Manual controller FAW” and “Data
sheet and configuration FAW”) through RS232 (TxD, RxD). </p>

![GUI](https://user-images.githubusercontent.com/81442784/213761322-25e6a6d7-bf56-46ee-9c02-29aa5546188e.gif)
